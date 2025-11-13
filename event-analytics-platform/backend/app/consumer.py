import asyncio
import json
from aiokafka import AIOKafkaConsumer
from redis import asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime
from collections import defaultdict
from typing import Dict, Any

from app.config import settings
from app.utils import setup_logging, get_time_bucket, deserialize_event, parse_user_agent_string
from app.core.database import AsyncSessionLocal, init_db
from app.core.plugins import plugin_manager
from app.core.event_pipeline import EventPipeline
from app.plugins.analytics_plugin import AnalyticsPlugin
from app.models.events import Event as EventModel, EventAggregation, UserSession

logger = setup_logging()


class StreamProcessor:
    """
    Enhanced stream processor with:
    - Database persistence
    - Plugin architecture
    - Redis caching
    - Session tracking
    """
    
    def __init__(self):
        self.redis_client = None
        self.kafka_consumer = None
        self.db_session = None
        self.aggregations = defaultdict(lambda: defaultdict(int))
        self.session_cache = {}  # Cache for active sessions
    
    async def start(self):
        """Initialize all connections"""
        logger.info("StreamProcessor: Initializing...")
        
        # Initialize Database
        await init_db()
        logger.info("StreamProcessor: Database initialized")
        
        # Initialize Redis
        self.redis_client = await aioredis.from_url(
            f"redis://{settings.redis_host}:{settings.redis_port}",
            encoding="utf-8",
            decode_responses=True
        )
        await self.redis_client.ping()
        logger.info("StreamProcessor: Redis client connected")
        
        # Initialize Kafka consumer
        self.kafka_consumer = AIOKafkaConsumer(
            settings.kafka_topic,
            bootstrap_servers=settings.kafka_bootstrap_servers,
            group_id=settings.kafka_group_id,
            value_deserializer=lambda m: m.decode('utf-8'),
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            max_poll_records=100
        )
        await self.kafka_consumer.start()
        logger.info(f"StreamProcessor: Kafka consumer started on topic '{settings.kafka_topic}'")
        
        # Register and initialize plugins
        analytics_plugin = AnalyticsPlugin()
        plugin_manager.register_plugin(analytics_plugin)
        await plugin_manager.startup()
        logger.info(f"StreamProcessor: Initialized {len(plugin_manager.plugins)} plugins")
    
    async def stop(self):
        """Cleanup connections"""
        logger.info("StreamProcessor: Shutting down...")
        
        # Shutdown plugins
        await plugin_manager.shutdown()
        
        if self.kafka_consumer:
            await self.kafka_consumer.stop()
        
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("StreamProcessor: Connections closed")
    
    async def store_event_in_db(self, event_data: Dict[str, Any]) -> EventModel:
        """
        Store event in PostgreSQL database
        
        Args:
            event_data: Event dictionary
        
        Returns:
            Stored event model
        """
        async with AsyncSessionLocal() as session:
            try:
                # Parse user agent if present
                user_agent = event_data.get("metadata", {}).get("user_agent", "Unknown")
                ua_info = parse_user_agent_string(user_agent)
                
                # Create event model
                event = EventModel(
                    event_id=event_data["event_id"],
                    type=event_data["type"],
                    timestamp=datetime.fromisoformat(
                        event_data["timestamp"].replace("Z", "+00:00")
                    ),
                    source=event_data["source"],
                    properties=event_data.get("properties", {}),
                    ip=event_data.get("metadata", {}).get("ip", "0.0.0.0"),
                    user_agent=user_agent,
                    user_id=event_data.get("user_id"),
                    session_id=event_data.get("session_id"),
                    processed=False
                )
                
                session.add(event)
                await session.commit()
                await session.refresh(event)
                
                return event
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to store event in DB: {e}", extra={
                    "event_id": event_data.get("event_id"),
                    "error": str(e)
                })
                raise
    
    async def update_session(self, event_data: Dict[str, Any]):
        """
        Update or create user session
        
        Args:
            event_data: Event dictionary
        """
        session_id = event_data.get("session_id")
        if not session_id:
            return
        
        async with AsyncSessionLocal() as session:
            try:
                # Check if session exists
                result = await session.execute(
                    select(UserSession).where(UserSession.session_id == session_id)
                )
                user_session = result.scalar_one_or_none()
                
                # Parse user agent
                user_agent = event_data.get("metadata", {}).get("user_agent", "Unknown")
                ua_info = parse_user_agent_string(user_agent)
                
                if user_session:
                    # Update existing session
                    user_session.last_activity_at = datetime.utcnow()
                    user_session.event_count += 1
                    
                    # Update event type counters
                    event_type = event_data.get("type")
                    if event_type == "page_view":
                        user_session.page_views += 1
                        # Update exit page
                        page = event_data.get("properties", {}).get("page")
                        if page:
                            user_session.exit_page = page
                    elif event_type == "click":
                        user_session.clicks += 1
                    elif event_type in ["purchase", "signup"]:
                        user_session.conversions += 1
                    
                    # Calculate duration
                    if user_session.started_at:
                        duration = (user_session.last_activity_at - user_session.started_at).total_seconds()
                        user_session.duration_seconds = int(duration)
                
                else:
                    # Create new session
                    page = event_data.get("properties", {}).get("page", "/")
                    
                    user_session = UserSession(
                        session_id=session_id,
                        user_id=event_data.get("user_id"),
                        started_at=datetime.utcnow(),
                        last_activity_at=datetime.utcnow(),
                        source=event_data.get("source"),
                        entry_page=page,
                        exit_page=page,
                        event_count=1,
                        page_views=1 if event_data.get("type") == "page_view" else 0,
                        clicks=1 if event_data.get("type") == "click" else 0,
                        conversions=1 if event_data.get("type") in ["purchase", "signup"] else 0,
                        device_type="mobile" if ua_info.get("is_mobile") else "desktop",
                        browser=ua_info.get("browser", "Unknown"),
                        os=ua_info.get("os", "Unknown"),
                        ip=event_data.get("metadata", {}).get("ip", "0.0.0.0"),
                        properties={}
                    )
                    session.add(user_session)
                
                await session.commit()
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to update session: {e}", extra={
                    "session_id": session_id,
                    "error": str(e)
                })
    
    async def update_aggregations(self, event_data: Dict[str, Any]):
        """
        Update aggregations in both Redis and PostgreSQL
        
        Args:
            event_data: Event dictionary
        """
        try:
            # Parse timestamp
            timestamp = datetime.fromisoformat(event_data['timestamp'].replace('Z', '+00:00'))
            event_type = event_data['type']
            source = event_data['source']
            session_id = event_data.get('session_id')
            user_id = event_data.get('user_id')
            
            # Get time bucket
            time_bucket = get_time_bucket(timestamp, settings.aggregation_window_seconds)
            time_bucket_dt = datetime.strptime(time_bucket, "%Y-%m-%dT%H:%M")
            
            # Update Redis (for real-time dashboard)
            pipe = self.redis_client.pipeline()
            
            # Total events counter
            pipe.incr("total_events")
            
            # Events per type
            pipe.hincrby("event_types", event_type, 1)
            
            # Per-minute aggregation
            agg_key = f"agg:{time_bucket}"
            pipe.hincrby(agg_key, event_type, 1)
            pipe.expire(agg_key, 3600)  # Expire after 1 hour
            
            # Track unique sessions
            if session_id:
                pipe.sadd(f"sessions:{time_bucket}", session_id)
                pipe.expire(f"sessions:{time_bucket}", 3600)
            
            # Track unique users
            if user_id:
                pipe.sadd(f"users:{time_bucket}", user_id)
                pipe.expire(f"users:{time_bucket}", 3600)
            
            await pipe.execute()
            
            # Get updated counts for pub/sub
            total_events = await self.redis_client.get("total_events")
            events_per_type = await self.redis_client.hgetall("event_types")
            current_count = await self.redis_client.hget(agg_key, event_type)
            
            # Publish to WebSocket subscribers
            update = {
                "event_type": event_type,
                "minute": time_bucket,
                "count": int(current_count),
                "total_events": int(total_events),
                "events_per_type": {k: int(v) for k, v in events_per_type.items()},
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await self.redis_client.publish(
                settings.redis_pubsub_channel,
                json.dumps(update)
            )
            
            # Update PostgreSQL aggregations
            await self.update_db_aggregations(
                time_bucket_dt, event_type, source, session_id, user_id
            )
            
        except Exception as e:
            logger.error(f"Failed to update aggregations: {e}", extra={
                "event": event_data,
                "error": str(e)
            })
    
    async def update_db_aggregations(
        self,
        time_bucket: datetime,
        event_type: str,
        source: str,
        session_id: str = None,
        user_id: str = None
    ):
        """
        Update aggregations in PostgreSQL database
        
        Args:
            time_bucket: Time bucket datetime
            event_type: Type of event
            source: Event source
            session_id: Optional session ID
            user_id: Optional user ID
        """
        async with AsyncSessionLocal() as session:
            try:
                # Check if aggregation exists
                result = await session.execute(
                    select(EventAggregation).where(
                        EventAggregation.time_bucket == time_bucket,
                        EventAggregation.event_type == event_type,
                        EventAggregation.source == source
                    )
                )
                aggregation = result.scalar_one_or_none()
                
                if aggregation:
                    # Update existing aggregation
                    aggregation.count += 1
                    aggregation.updated_at = datetime.utcnow()
                    
                    # Update unique counts (simplified - in production use HyperLogLog)
                    if session_id:
                        aggregation.unique_sessions += 1
                    if user_id:
                        aggregation.unique_users += 1
                else:
                    # Create new aggregation
                    aggregation = EventAggregation(
                        time_bucket=time_bucket,
                        window_size=settings.aggregation_window_seconds,
                        event_type=event_type,
                        source=source,
                        count=1,
                        unique_sessions=1 if session_id else 0,
                        unique_users=1 if user_id else 0
                    )
                    session.add(aggregation)
                
                await session.commit()
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to update DB aggregations: {e}")
    
    async def process_event(self, event_data: Dict[str, Any]):
        """
        Complete event processing pipeline:
        1. Store in database
        2. Update session
        3. Update aggregations
        4. Process through plugins
        5. Publish to pub/sub
        """
        try:
            # Enrich event
            enriched_event = EventPipeline.enrich_event(event_data)
            
            # Store in database
            db_event = await self.store_event_in_db(enriched_event)
            logger.info(f"Event stored in DB: {db_event.event_id}")
            
            # Update session tracking
            await self.update_session(enriched_event)
            
            # Update aggregations
            await self.update_aggregations(enriched_event)
            
            # Process through plugins
            plugin_results = await plugin_manager.process_event(enriched_event)
            
            # Log plugin results
            for plugin_name, result in plugin_results.items():
                if result.success:
                    logger.info(f"Plugin '{plugin_name}' processed successfully", extra={
                        "event_id": enriched_event["event_id"],
                        "plugin_data": result.data
                    })
                else:
                    logger.error(f"Plugin '{plugin_name}' failed", extra={
                        "event_id": enriched_event["event_id"],
                        "error": result.error
                    })
            
            # Mark event as processed in DB
            async with AsyncSessionLocal() as session:
                await session.execute(
                    update(EventModel)
                    .where(EventModel.event_id == enriched_event["event_id"])
                    .values(processed=True)
                )
                await session.commit()
            
        except Exception as e:
            logger.error(f"Failed to process event: {e}", extra={
                "event": event_data,
                "error": str(e)
            })
    
    async def consume_loop(self):
        """Main consumption loop"""
        logger.info("StreamProcessor: Starting consumption loop...")
        
        try:
            async for message in self.kafka_consumer:
                try:
                    event_data = deserialize_event(message.value)
                    await self.process_event(event_data)
                    
                except Exception as e:
                    logger.error(f"Error processing message: {e}", extra={
                        "message": message.value,
                        "error": str(e)
                    })
        
        except Exception as e:
            logger.error(f"Consumer loop error: {e}", exc_info=True)
        
        finally:
            await self.stop()


async def main():
    """Main entry point for the consumer"""
    processor = StreamProcessor()
    
    try:
        await processor.start()
        logger.info("✅ StreamProcessor started successfully")
        await processor.consume_loop()
        
    except KeyboardInterrupt:
        logger.info("StreamProcessor: Received shutdown signal")
        await processor.stop()
        
    except Exception as e:
        logger.error(f"StreamProcessor: Fatal error - {e}", exc_info=True)
        await processor.stop()


if __name__ == "__main__":
    asyncio.run(main())