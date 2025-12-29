from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from datetime import datetime, timedelta
import uuid

from app.core.database import get_db
from app.core.kafka_producer import kafka_producer
from app.core.schema_engine import SchemaEngine
from app.models.schemas import Schema
from app.models.adaptors import Adaptor
from app.models.events import EventLog
from app.schemas_pydantic import EventIngest, EventResponse, EventStatsResponse
from app.config import settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/events", tags=["events"], redirect_slashes=True)


@router.post("/ingest", response_model=EventResponse)
async def ingest_event(
    event: EventIngest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Ingest an event from tag manager
    Validates against schema and stores in appropriate table
    """
    try:
        # Get client IP
        client_ip = request.client.host
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        
        # Add IP to metadata
        event_metadata = event.metadata.copy()
        event_metadata["ip"] = client_ip
        event_metadata["user_agent"] = request.headers.get("User-Agent", "Unknown")
        
        # Verify schema exists
        result = await db.execute(
            select(Schema).where(Schema.name == event.schema_id)
        )
        schema = result.scalar_one_or_none()
        
        if not schema:
            raise HTTPException(status_code=404, detail=f"Schema '{event.schema_id}' not found")
        
        if not schema.active:
            raise HTTPException(status_code=400, detail=f"Schema '{event.schema_id}' is inactive")
        
        # Validate event against schema
        event_data_dict = {
            "event_type": event.event_type,
            "properties": event.properties
        }
        
        is_valid, error_msg = SchemaEngine.validate_event_against_schema(
            event_data_dict,
            schema.properties
        )
        
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Event validation failed: {error_msg}")
        
        # Generate event ID
        event_id = str(uuid.uuid4())
        
        # Prepare event data
        full_event_data = {
            "event_type": event.event_type,
            "user_id": event.user_id,
            "session_id": event.session_id,
            "timestamp": event.timestamp,
            "properties": event.properties,
            "metadata": event_metadata  # Use 'metadata' here for schema table
        }
        
        # Store in schema-specific table FIRST
        await SchemaEngine.insert_event(db, event.schema_id, full_event_data)
        
        # Store in master event log (same session, after schema table succeeds)
        event_log = EventLog(
            event_id=event_id,
            schema_id=event.schema_id,
            event_type=event.event_type,
            user_id=event.user_id,
            session_id=event.session_id,
            timestamp=event.timestamp,
            properties=event.properties,
            event_metadata=event_metadata,
            container_id=event.properties.get("container_id"),
            processed=1
        )
        
        db.add(event_log)
        await db.commit()  # Commit both tables together
        
        # Send to Kafka (non-blocking)
        try:
            kafka_event = {
                "event_id": event_id,
                "schema_id": event.schema_id,
                "event_type": event.event_type,
                "user_id": event.user_id,
                "session_id": event.session_id,
                "timestamp": event.timestamp.isoformat(),
                "properties": event.properties,
                "metadata": event_metadata
            }
            await kafka_producer.send_event(settings.kafka_topic_events, kafka_event)
        except Exception as kafka_error:
            logger.warning(f"Kafka send failed (non-critical): {kafka_error}")
        
        # Update adaptor stats (non-critical)
        try:
            if event.properties.get("container_id"):
                container_id = event.properties["container_id"]
                result = await db.execute(
                    select(Adaptor).where(Adaptor.container_id == container_id)
                )
                adaptor = result.scalar_one_or_none()
                if adaptor:
                    adaptor.total_events["count"] = adaptor.total_events.get("count", 0) + 1
                    await db.commit()
        except Exception as adaptor_error:
            logger.warning(f"Failed to update adaptor stats: {adaptor_error}")
        
        return EventResponse(
            status="success",
            event_id=event_id,
            message="Event ingested successfully"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"INGESTION ERROR: {str(e)}", exc_info=True)
        logger.error(f"Event data: schema_id={event.schema_id}, event_type={event.event_type}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

@router.get("/stats", response_model=EventStatsResponse)
async def get_event_stats(
    schema_id: str = None,
    days: int = 7,
    db: AsyncSession = Depends(get_db)
):
    """Get event statistics"""
    try:
        time_filter = datetime.utcnow() - timedelta(days=days)
        
        # Total events
        query = select(func.count(EventLog.id))
        if schema_id:
            query = query.where(EventLog.schema_id == schema_id)
        query = query.where(EventLog.timestamp >= time_filter)
        
        result = await db.execute(query)
        total_events = result.scalar() or 0
        
        # Events by schema
        query = select(
            EventLog.schema_id,
            func.count(EventLog.id).label('count')
        ).where(EventLog.timestamp >= time_filter).group_by(EventLog.schema_id)
        
        result = await db.execute(query)
        events_by_schema = {row[0]: row[1] for row in result.fetchall()}
        
        # Events by type
        query = select(
            EventLog.event_type,
            func.count(EventLog.id).label('count')
        ).where(EventLog.timestamp >= time_filter)
        
        if schema_id:
            query = query.where(EventLog.schema_id == schema_id)
        
        query = query.group_by(EventLog.event_type)
        
        result = await db.execute(query)
        events_by_type = {row[0]: row[1] for row in result.fetchall()}
        
        # Calculate page views
        page_views = sum(count for event_type, count in events_by_type.items() 
                        if 'page_view' in event_type.lower())
        
        # Calculate clicks
        clicks = sum(count for event_type, count in events_by_type.items() 
                    if 'click' in event_type.lower())
        
        # Unique sessions
        query = select(func.count(func.distinct(EventLog.session_id)))
        if schema_id:
            query = query.where(EventLog.schema_id == schema_id)
        query = query.where(EventLog.timestamp >= time_filter)
        
        result = await db.execute(query)
        unique_sessions = result.scalar() or 0
        
        # Recent events (last hour)
        recent_time = datetime.utcnow() - timedelta(hours=1)
        query = select(func.count(EventLog.id)).where(EventLog.timestamp >= recent_time)
        if schema_id:
            query = query.where(EventLog.schema_id == schema_id)
        
        result = await db.execute(query)
        recent_events = result.scalar() or 0
        
        return EventStatsResponse(
            total_events=total_events,
            events_by_schema=events_by_schema,
            events_by_type=events_by_type,
            recent_events=recent_events,
            page_views=page_views,
            clicks=clicks,
            unique_sessions=unique_sessions
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")
@router.get("/recent")
async def get_recent_events(
    schema_id: str = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """Get recent events"""
    try:
        query = select(EventLog)
        
        if schema_id:
            query = query.where(EventLog.schema_id == schema_id)
        
        query = query.order_by(EventLog.timestamp.desc()).limit(limit)
        
        result = await db.execute(query)
        events = result.scalars().all()
        
        return {
            "events": [e.to_dict() for e in events],
            "count": len(events)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recent events: {str(e)}")