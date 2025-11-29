from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Any, Optional, List


class AdaptorCreate(BaseModel):
    """Create adaptor request"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    schema_id: str = Field(..., description="Schema name this adaptor uses")
    website_url: str = Field(..., description="Website URL to track")
    allowed_domains: List[str] = Field(default_factory=list, description="Allowed domains for CORS")
    tracking_rules: Dict[str, Any] = Field(
        default_factory=lambda: {
            "auto_page_view": True,
            "track_clicks": True,
            "track_forms": False
        },
        description="Tracking configuration"
    )
    custom_code: Optional[str] = Field(None, description="Custom JavaScript tracking code")


class AdaptorUpdate(BaseModel):
    """Update adaptor request"""
    name: Optional[str] = None
    description: Optional[str] = None
    website_url: Optional[str] = None
    allowed_domains: Optional[List[str]] = None
    tracking_rules: Optional[Dict[str, Any]] = None
    custom_code: Optional[str] = None
    active: Optional[bool] = None


class AdaptorResponse(BaseModel):
    """Adaptor response model"""
    id: str
    container_id: str
    name: str
    description: Optional[str]
    schema_id: str
    website_url: str
    allowed_domains: List[str]
    tracking_rules: Dict[str, Any]
    active: bool
    created_at: str
    updated_at: str
    total_events: Dict[str, Any]
    
    model_config = ConfigDict(from_attributes=True)


class AdaptorListResponse(BaseModel):
    """List of adaptors response"""
    adaptors: list[AdaptorResponse]
    total: int


class ContainerCodeResponse(BaseModel):
    """Container code snippet response"""
    container_id: str
    script_url: str
    installation_code: str