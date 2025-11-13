import json
import logging
from datetime import datetime
from typing import Optional
from pythonjsonlogger import jsonlogger
from user_agents import parse as parse_user_agent


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


def parse_user_agent_string(user_agent: str) -> dict:
    """
    Parse user agent string to extract browser, device, and OS info
    
    Args:
        user_agent: User agent string
    
    Returns:
        Dictionary with parsed information
    """
    try:
        ua = parse_user_agent(user_agent)
        return {
            "browser": ua.browser.family,
            "browser_version": ua.browser.version_string,
            "os": ua.os.family,
            "os_version": ua.os.version_string,
            "device": ua.device.family,
            "is_mobile": ua.is_mobile,
            "is_tablet": ua.is_tablet,
            "is_pc": ua.is_pc,
            "is_bot": ua.is_bot,
        }
    except Exception as e:
        return {
            "browser": "Unknown",
            "os": "Unknown",
            "device": "Unknown",
            "error": str(e)
        }


def calculate_session_metrics(events: list) -> dict:
    """
    Calculate session metrics from a list of events
    
    Args:
        events: List of event dictionaries
    
    Returns:
        Dictionary with session metrics
    """
    if not events:
        return {
            "total_events": 0,
            "duration_seconds": 0,
            "page_views": 0,
            "clicks": 0,
        }
    
    # Sort by timestamp
    sorted_events = sorted(events, key=lambda e: e.get("timestamp", ""))
    
    # Calculate duration
    start_time = datetime.fromisoformat(sorted_events[0]["timestamp"].replace("Z", "+00:00"))
    end_time = datetime.fromisoformat(sorted_events[-1]["timestamp"].replace("Z", "+00:00"))
    duration = (end_time - start_time).total_seconds()
    
    # Count event types
    event_counts = {}
    for event in events:
        event_type = event.get("type", "unknown")
        event_counts[event_type] = event_counts.get(event_type, 0) + 1
    
    return {
        "total_events": len(events),
        "duration_seconds": int(duration),
        "page_views": event_counts.get("page_view", 0),
        "clicks": event_counts.get("click", 0),
        "purchases": event_counts.get("purchase", 0),
        "signups": event_counts.get("signup", 0),
        "event_type_breakdown": event_counts,
    }


def sanitize_properties(properties: dict, max_depth: int = 3) -> dict:
    """
    Sanitize event properties to prevent deeply nested objects
    
    Args:
        properties: Properties dictionary
        max_depth: Maximum nesting depth allowed
    
    Returns:
        Sanitized properties
    """
    def _sanitize(obj, depth=0):
        if depth >= max_depth:
            return str(obj)
        
        if isinstance(obj, dict):
            return {k: _sanitize(v, depth + 1) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [_sanitize(item, depth + 1) for item in obj[:100]]  # Limit list size
        else:
            return obj
    
    return _sanitize(properties)