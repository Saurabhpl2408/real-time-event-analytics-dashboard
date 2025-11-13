from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Any, Literal, Optional, List
from datetime import datetime
import uuid


class EventMetadata(BaseModel):
    ip: str = "0.0.0.0"
    user_agent: str = "Unknown"


class Event(BaseModel):
    """Event schema for ingestion"""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: Literal["page_view", "click", "trade", "purchase", "signup", "custom"]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: Literal["web", "api", "mobile", "external"]
    properties: Dict[str, Any] = Field(default_factory=dict)
    metadata: EventMetadata = Field(default_factory=EventMetadata)
    user_id: Optional[str] = None
    session_id: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "event_id": "b7b7c9fa-7321-4e1b-8217-1a9a7f8c43a1",
                "type": "page_view",
                "timestamp": "2025-10-15T18:00:00Z",
                "source": "web",
                "properties": {"page": "/home"},
                "metadata": {"ip": "127.0.0.1", "user_agent": "Mozilla/5.0"},
                "user_id": "user_123",
                "session_id": "session_456"
            }
        }
    )


class EventResponse(BaseModel):
    """Response after event ingestion"""
    status: str
    event_id: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AggregatedMetric(BaseModel):
    """Aggregated metric response"""
    time_bucket: datetime
    event_type: str
    count: int
    unique_users: int
    unique_sessions: int
    source: Optional[str] = None


class DashboardUpdate(BaseModel):
    """Real-time dashboard update via WebSocket"""
    event_type: str
    minute: str
    count: int
    total_events: int
    events_per_type: Dict[str, int]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class StatsResponse(BaseModel):
    """Statistics response"""
    total_events: int
    events_per_type: Dict[str, int]
    recent_aggregations: List[Dict[str, Any]]
    unique_sessions: int
    unique_users: int
    time_range: Optional[Dict[str, str]] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    kafka: str
    redis: str
    database: str
    active_connections: int
    plugins: List[str]


class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=1000)


class EventListResponse(BaseModel):
    """Paginated event list response"""
    events: List[Dict[str, Any]]
    total: int
    page: int
    page_size: int
    total_pages: int


class TimeRangeParams(BaseModel):
    """Time range filter parameters"""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    event_type: Optional[str] = None
    source: Optional[str] = None


class PluginInfo(BaseModel):
    """Plugin information"""
    name: str
    enabled: bool
    priority: str
    topics: List[str]


class PluginListResponse(BaseModel):
    """List of registered plugins"""
    plugins: List[PluginInfo]
    total: int