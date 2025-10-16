import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Redis Configuration
    redis_host: str = os.getenv("REDIS_HOST", "localhost")
    redis_port: int = int(os.getenv("REDIS_PORT", "6379"))
    redis_pubsub_channel: str = "realtime_updates"
    
    # Kafka Configuration
    kafka_bootstrap_servers: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:19092")
    kafka_topic: str = os.getenv("KAFKA_TOPIC", "events.raw")
    kafka_group_id: str = os.getenv("KAFKA_GROUP_ID", "analytics-consumer-group")
    
    # Backend Configuration
    backend_host: str = os.getenv("BACKEND_HOST", "0.0.0.0")
    backend_port: int = int(os.getenv("BACKEND_PORT", "8000"))
    
    # Aggregation window (seconds)
    aggregation_window_seconds: int = 60
    
    class Config:
        env_file = ".env"

settings = Settings()