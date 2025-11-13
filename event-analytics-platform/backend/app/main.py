from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from aiokafka import AIOKafkaProducer
from redis import asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import json
from typing import Set
from datetime import datetime, timedelta

from app.schemas import (
    Event, EventResponse, StatsResponse, 
    HealthResponse, PluginListResponse, PluginInfo
)
from app.config import settings
from app.utils import setup_logging, serialize_event
from app.core.database import get_db, init_db, engine
from app.core.plugins import plugin_manager
from app.core.event_pipeline import EventPipeline
from app.plugins.analytics_plugin import AnalyticsPlugin
from app.models.events import Event as EventModel, EventAggregation

# Setup logging
logger = setup_logging()

# FastAPI app
app = FastAPI(
    title="InsightFlow Analytics API",
    version="1.0.0",
    description="Real-time event analytics platform with extensible plugin architecture"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global connections
kafka_producer: AIOKafkaProducer = None
redis_client: aioredis.Redis = None
active_websockets: Set[WebSocket] = set()


@app.on_event("startup")
async def startup_event():
    """Initialize all services"""
    global kafka_producer, redis_client
    
    logger.info("Starting InsightFlow Analytics API...")
    
    try:
        # Initialize database
        await init_db()
        logger.info("Database initialized")
        
        # Enable TimescaleDB hypertable (if not already)
        if settings.enable_timescaledb:
            try:
                async with engine.begin() as conn:
                    await conn.execute(
                        text(
                            "SELECT create_hypertable('events', 'timestamp', "
                            "if_not_exists => TRUE, "
                            f"chunk_time_interval => INTERVAL '{settings.timescale_chunk_interval}');"
                        )
                    )
                    logger.info("TimescaleDB hypertable enabled for events table")
            except Exception as e:
                logger.warning(f"TimescaleDB setup warning (may already exist): {e}")
        
        # Initialize Kafka producer
        kafka_producer = AIOKafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers,
            value_serializer=lambda v: v.encode('utf-8')
        )
        await kafka_producer.start()
        logger.info(f"Kafka producer started: {settings.kafka_bootstrap_servers}")
        
        # Initialize Redis client
        redis_client = await aioredis.from_url(
            f"redis://{settings.redis_host}:{settings.redis_port}",
            encoding="utf-8",
            decode_responses=True
        )
        await redis_client.ping()
        logger.info(f"Redis client connected: {settings.redis_host}:{settings.redis_port}")
        
        # Register plugins
        analytics_plugin = AnalyticsPlugin()
        plugin_manager.register_plugin(analytics_plugin)
        
        # Initialize plugins
        await plugin_manager.startup()
        logger.info(f"Registered {len(plugin_manager.plugins)} plugins")
        
        logger.info("✅ InsightFlow API started successfully")
        
    except Exception as e:
        logger.error(f"Startup failed: {e}", exc_info=True)
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup connections"""
    global kafka_producer, redis_client
    
    logger.info("Shutting down InsightFlow API...")
    
    # Shutdown plugins
    await plugin_manager.shutdown()
    
    if kafka_producer:
        await kafka_producer.stop()
        logger.info("Kafka producer stopped")
    
    if redis_client:
        await redis_client.close()
        logger.info("Redis client closed")
    
    logger.info("✅ InsightFlow API shutdown complete")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "InsightFlow Analytics API",
        "version": "1.0.0",
        "status": "running",
        "environment": settings.environment,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health", response_model=HealthResponse)
async def health_check(db: AsyncSession = Depends(get_db)):
    """Comprehensive health check"""
    kafka_healthy = kafka_producer is not None
    redis_healthy = False
    db_healthy = False
    
    # Check Redis
    try:
        await redis_client.ping()
        redis_healthy = True
    except:
        pass
    
    # Check Database
    try:
        result = await db.execute(select(func.count()).select_from(EventModel))
        db_healthy = True
    except:
        pass
    
    overall_status = "healthy" if (kafka_healthy and redis_healthy and db_healthy) else "degraded"
    
    return HealthResponse(
        status=overall_status,
        kafka="connected" if kafka_healthy else "disconnected",
        redis="connected" if redis_healthy else "disconnected",
        database="connected" if db_healthy else "disconnected",
        active_connections=len(active_websockets),
        plugins=[p.name for p in plugin_manager.plugins]
    )


@app.get("/plugins", response_model=PluginListResponse)
async def list_plugins():
    """List all registered plugins"""
    plugins_info = plugin_manager.list_plugins()
    return PluginListResponse(
        plugins=[PluginInfo(**p) for p in plugins_info],
        total=len(plugins_info)
    )

@app.get("/stats", response_model=StatsResponse)
async def get_stats(db: AsyncSession = Depends(get_db)):
    """Get current statistics"""
    try:
        # Get total event count from Redis
        total_events = await redis_client.get("total_events") or 0
        
        # Get events per type from Redis
        event_types = await redis_client.hgetall("event_types")
        
        # Get recent aggregations from Redis
        recent_minutes = []
        keys = await redis_client.keys("agg:*")
        for key in keys[-10:]:
            data = await redis_client.hgetall(key)
            if data:
                recent_minutes.append(data)
        
        # Get unique sessions/users count from database
        unique_sessions_result = await db.execute(
            select(func.count(func.distinct(EventModel.session_id)))
            .where(EventModel.timestamp >= datetime.utcnow() - timedelta(hours=24))
        )
        unique_sessions = unique_sessions_result.scalar() or 0
        
        unique_users_result = await db.execute(
            select(func.count(func.distinct(EventModel.user_id)))
            .where(EventModel.timestamp >= datetime.utcnow() - timedelta(hours=24))
            .where(EventModel.user_id.isnot(None))
        )
        unique_users = unique_users_result.scalar() or 0
        
        return StatsResponse(
            total_events=int(total_events),
            events_per_type={k: int(v) for k, v in event_types.items()},
            recent_aggregations=recent_minutes,
            unique_sessions=unique_sessions,
            unique_users=unique_users
        )
    
    except Exception as e:
        logger.error(f"Failed to fetch stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch statistics")


@app.post("/ingest", response_model=EventResponse)
async def ingest_event(event: Event):
    """
    Ingest a single event
    Validates, enriches, and publishes to Kafka
    """
    try:
        # Convert to dict
        event_dict = event.model_dump()
        
        # Validate event
        is_valid, error = EventPipeline.validate_event(event_dict)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error)
        
        # Enrich event
        enriched_event = EventPipeline.enrich_event(event_dict)
        
        # Serialize event
        event_json = serialize_event(enriched_event)
        
        # Determine routing
        topic = EventPipeline.route_event(enriched_event)
        
        # Send to Kafka
        await kafka_producer.send_and_wait(topic, value=event_json)
        
        logger.info("Event ingested", extra={
            "event_id": event.event_id,
            "event_type": event.type,
            "source": event.source,
            "topic": topic
        })
        
        return EventResponse(
            status="success",
            event_id=event.event_id,
            message="Event ingested successfully"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to ingest event", extra={
            "error": str(e),
            "event_id": event.event_id
        })
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time dashboard updates"""
    await websocket.accept()
    active_websockets.add(websocket)
    
    logger.info(f"WebSocket client connected (total: {len(active_websockets)})")
    
    # Create Redis pub/sub client
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(settings.redis_pubsub_channel)
    
    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                await websocket.send_text(message["data"])
    
    except WebSocketDisconnect:
        active_websockets.remove(websocket)
        await pubsub.unsubscribe(settings.redis_pubsub_channel)
        await pubsub.close()
        logger.info(f"WebSocket client disconnected (total: {len(active_websockets)})")
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")

from sqlalchemy import text        