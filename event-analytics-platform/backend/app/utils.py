import json
import logging
from datetime import datetime
from pythonjsonlogger import jsonlogger

def setup_logging():
    """Configure structured JSON logging"""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    logHandler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s',
        timestamp=True
    )
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
    
    return logger

def get_time_bucket(timestamp: datetime, window_seconds: int = 60) -> str:
    """
    Round timestamp to the nearest time bucket
    Default: minute-level buckets
    """
    epoch = int(timestamp.timestamp())
    bucket_epoch = (epoch // window_seconds) * window_seconds
    return datetime.fromtimestamp(bucket_epoch).strftime("%Y-%m-%dT%H:%M")

def serialize_event(event_dict: dict) -> str:
    """Serialize event to JSON string for Kafka"""
    # Convert datetime to ISO format string
    if isinstance(event_dict.get('timestamp'), datetime):
        event_dict['timestamp'] = event_dict['timestamp'].isoformat()
    return json.dumps(event_dict)

def deserialize_event(event_str: str) -> dict:
    """Deserialize event from JSON string"""
    return json.loads(event_str)