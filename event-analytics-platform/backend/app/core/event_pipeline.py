from typing import Dict, Any, Optional
from datetime import datetime
import hashlib
import json


class EventPipeline:
    """
    Event processing pipeline
    Handles event validation, enrichment, and routing
    """
    
    @staticmethod
    def generate_session_id(ip: str, user_agent: str) -> str:
        """Generate a session ID based on IP and user agent"""
        data = f"{ip}:{user_agent}:{datetime.utcnow().date()}"
        return hashlib.md5(data.encode()).hexdigest()
    
    @staticmethod
    def extract_user_info(metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Extract user information from metadata"""
        return {
            "ip": metadata.get("ip", "0.0.0.0"),
            "user_agent": metadata.get("user_agent", "Unknown"),
        }
    
    @staticmethod
    def enrich_event(event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich event with additional computed fields
        
        Args:
            event: Raw event data
        
        Returns:
            Enriched event
        """
        enriched = event.copy()
        
        # Generate session ID if not present
        if "session_id" not in enriched:
            metadata = enriched.get("metadata", {})
            ip = metadata.get("ip", "0.0.0.0")
            user_agent = metadata.get("user_agent", "Unknown")
            enriched["session_id"] = EventPipeline.generate_session_id(ip, user_agent)
        
        # Add processing timestamp
        enriched["processed_at"] = datetime.utcnow().isoformat()
        
        # Extract page information if present
        if enriched.get("type") == "page_view":
            properties = enriched.get("properties", {})
            if "page" in properties:
                enriched["page_url"] = properties["page"]
        
        return enriched
    
    @staticmethod
    def validate_event(event: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate event structure
        
        Args:
            event: Event to validate
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        required_fields = ["event_id", "type", "timestamp", "source"]
        
        for field in required_fields:
            if field not in event:
                return False, f"Missing required field: {field}"
        
        # Validate event type
        valid_types = ["page_view", "click", "trade", "purchase", "signup", "custom"]
        if event["type"] not in valid_types:
            return False, f"Invalid event type: {event['type']}"
        
        # Validate source
        valid_sources = ["web", "api", "mobile", "external"]
        if event["source"] not in valid_sources:
            return False, f"Invalid source: {event['source']}"
        
        return True, None
    
    @staticmethod
    def route_event(event: Dict[str, Any]) -> str:
        """
        Determine which Kafka topic to route the event to
        
        Args:
            event: Event data
        
        Returns:
            Kafka topic name
        """
        event_type = event.get("type", "custom")
        
        # Route based on event type
        routing_map = {
            "page_view": "events.raw",
            "click": "events.raw",
            "purchase": "events.raw",
            "signup": "events.raw",
            "trade": "events.raw",
            "custom": "events.raw",
        }
        
        return routing_map.get(event_type, "events.raw")