from aiokafka import AIOKafkaProducer
from app.config import settings
import json
import logging

logger = logging.getLogger(__name__)


class KafkaProducerManager:
    """Kafka producer manager"""
    
    def __init__(self):
        self.producer = None
    
    async def start(self):
        """Start Kafka producer"""
        self.producer = AIOKafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            compression_type='gzip'
        )
        await self.producer.start()
        logger.info(f"✅ Kafka producer started: {settings.kafka_bootstrap_servers}")
    
    async def stop(self):
        """Stop Kafka producer"""
        if self.producer:
            await self.producer.stop()
            logger.info("Kafka producer stopped")
    
    async def send_event(self, topic: str, event: dict):
        """Send event to Kafka"""
        try:
            await self.producer.send_and_wait(topic, value=event)
            return True
        except Exception as e:
            logger.error(f"Failed to send event to Kafka: {e}")
            return False


# Global instance
kafka_producer = KafkaProducerManager()