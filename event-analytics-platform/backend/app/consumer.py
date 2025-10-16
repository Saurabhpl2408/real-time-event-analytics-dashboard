import asyncio
import json
from aiokafka import AIOKafkaConsumer
from redis import asyncio as aioredis
from datetime import datetime
from collections import defaultdict

from app.config import settings
from app.utils import setup_logging, get_time_bucket, deserialize_event

logger = setup_logging()

class StreamProcessor:
    def __init__(self):
        self.redis_client = None
        self.kafka_consumer = None
        self.aggregations = defaultdict(lambda: defaultdict(int))
    
    async def start(self):
        """Initialize connections"""
        # Initialize Redis
        self.redis_client = await aioredis.from_url(
            f"redis://{settings.redis_host}:{settings.redis_port}",
            encoding="utf-8",
            decode_responses=True
        )
        logger.info("Consumer: Redis client connected")
        
        # Initialize Kafka consumer
        self.kafka_consumer = AIOKafkaConsumer(
            settings.kafka_topic,
            bootstrap_servers=settings.kafka_bootstrap_servers,
            group_id=settings.kafka_group_id,
            value_deserializer=lambda m: m.decode('utf-8'),
            auto_offset_reset='earliest',
            enable_auto_commit=True
        )
        await self.kafka_consumer.start()
        logger.info("Consumer: Kafka consumer started", extra={
            "topic": settings.kafka_topic,
            "group_id": settings.kafka_group_id
        })
    
    async def stop(self):
        """Cleanup connections"""
        if self.kafka_consumer:
            await self.kafka_consumer.stop()
        if self.redis_client:
            await self.redis_client.close()
        logger.info("Consumer: Connections closed")
    
    async def process_event(self, event_data: dict):
        """
        Process a single event:
        1. Enrich with time bucket
        2. Aggregate by minute and event type
        3. Store in Redis
        4. Publish update to Redis pub/sub
        """
        try:
            # Parse timestamp
            timestamp = datetime.fromisoformat(event_data['timestamp'].replace('Z', '+00:00'))
            event_type = event_data['type']
            
            # Get time bucket (minute)
            time_bucket = get_time_bucket(timestamp, settings.aggregation_window_seconds)
            
            # Increment counters in Redis
            pipe = self.redis_client.pipeline()
            
            # Total events counter
            pipe.incr("total_events")
            
            # Events per type
            pipe.hincrby("event_types", event_type, 1)
            
            # Per-minute aggregation
            agg_key = f"agg:{time_bucket}"
            pipe.hincrby(agg_key, event_type, 1)
            pipe.expire(agg_key, 3600)  # Expire after 1 hour
            
            await pipe.execute()
            
            # Get updated counts
            total_events = await self.redis_client.get("total_events")
            events_per_type = await self.redis_client.hgetall("event_types")
            current_count = await self.redis_client.hget(agg_key, event_type)
            
            # Prepare dashboard update
            update = {
                "event_type": event_type,
                "minute": time_bucket,
                "count": int(current_count),
                "total_events": int(total_events),
                "events_per_type": {k: int(v) for k, v in events_per_type.items()},
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Publish to Redis pub/sub
            await self.redis_client.publish(
                settings.redis_pubsub_channel,
                json.dumps(update)
            )
            
            logger.info("Event processed", extra={
                "event_type": event_type,
                "time_bucket": time_bucket,
                "total_events": total_events
            })
        
        except Exception as e:
            logger.error("Failed to process event", extra={
                "error": str(e),
                "event": event_data
            })
    
    async def consume_loop(self):
        """Main consumption loop"""
        logger.info("Consumer: Starting consumption loop")
        
        try:
            async for message in self.kafka_consumer:
                try:
                    event_data = deserialize_event(message.value)
                    await self.process_event(event_data)
                except Exception as e:
                    logger.error("Error processing message", extra={
                        "error": str(e),
                        "message": message.value
                    })
        
        except Exception as e:
            logger.error("Consumer loop error", extra={"error": str(e)})
        
        finally:
            await self.stop()

async def main():
    """Main entry point for the consumer"""
    processor = StreamProcessor()
    
    try:
        await processor.start()
        await processor.consume_loop()
    except KeyboardInterrupt:
        logger.info("Consumer: Shutting down gracefully")
        await processor.stop()
    except Exception as e:
        logger.error("Consumer: Fatal error", extra={"error": str(e)})
        await processor.stop()

if __name__ == "__main__":
    asyncio.run(main())