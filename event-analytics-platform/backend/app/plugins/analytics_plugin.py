from typing import Dict, Any, List
from datetime import datetime
from collections import defaultdict

from app.core.plugins import EventPlugin, PluginResult, PluginPriority


class AnalyticsPlugin(EventPlugin):
    """
    Analytics processing plugin
    Handles event aggregation and metrics calculation
    """
    
    def __init__(self):
        super().__init__(name="analytics", priority=PluginPriority.HIGH)
        self.event_counts = defaultdict(int)
        self.session_counts = defaultdict(set)
    
    async def process(self, event: Dict[str, Any]) -> PluginResult:
        """
        Process analytics for an event
        
        Calculates:
        - Event counts by type
        - Unique sessions
        - Time-based aggregations
        """
        try:
            event_type = event.get("type", "unknown")
            session_id = event.get("session_id")
            
            # Increment event count
            self.event_counts[event_type] += 1
            
            # Track unique sessions
            if session_id:
                self.session_counts[event_type].add(session_id)
            
            # Prepare analytics data
            analytics_data = {
                "event_type": event_type,
                "total_count": self.event_counts[event_type],
                "unique_sessions": len(self.session_counts[event_type]),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return PluginResult(
                success=True,
                data=analytics_data,
                metadata={
                    "plugin": self.name,
                    "processing_time_ms": 0  # Can add actual timing
                }
            )
        
        except Exception as e:
            return PluginResult(
                success=False,
                error=f"Analytics processing error: {str(e)}"
            )
    
    def get_kafka_topics(self) -> List[str]:
        """Subscribe to raw events topic"""
        return ["events.raw", "events.processed"]
    
    async def enrich_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Add analytics-specific enrichment"""
        enriched = event.copy()
        
        # Add analytics timestamp
        enriched["analytics_processed_at"] = datetime.utcnow().isoformat()
        
        # Calculate event age
        if "timestamp" in enriched:
            event_time = datetime.fromisoformat(
                enriched["timestamp"].replace("Z", "+00:00")
            )
            age_seconds = (datetime.utcnow().replace(tzinfo=event_time.tzinfo) - event_time).total_seconds()
            enriched["event_age_seconds"] = age_seconds
        
        return enriched
    
    def should_process(self, event: Dict[str, Any]) -> bool:
        """Process all events for analytics"""
        return self.enabled and event.get("type") is not None
    
    async def on_startup(self):
        """Initialize analytics plugin"""
        print(f"[{self.name}] Analytics plugin started")
        print(f"[{self.name}] Subscribed to topics: {self.get_kafka_topics()}")
    
    async def on_shutdown(self):
        """Cleanup analytics plugin"""
        print(f"[{self.name}] Analytics plugin stopped")
        print(f"[{self.name}] Final event counts: {dict(self.event_counts)}")