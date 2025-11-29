from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Any, Optional
from datetime import datetime


class SchemaCreate(BaseModel):
    """Schema for creating a new schema definition"""
    name: str = Field(..., min_length=1, max_length=100, description="Schema name (e.g., 'portfolio', 'ecommerce')")
    description: Optional[str] = Field(None, description="Schema description")
    properties: Dict[str, Dict[str, str]] = Field(
        ...,
        description="Event types and their properties",
        example={
            "page_view": {"page": "string", "referrer": "string"},
            "project_click": {"project_name": "string", "project_url": "string"}
        }
    )


class SchemaUpdate(BaseModel):
    """Schema for updating a schema"""
    name: Optional[str] = None
    description: Optional[str] = None
    properties: Optional[Dict[str, Dict[str, str]]] = None
    active: Optional[bool] = None


class SchemaResponse(BaseModel):
    """Schema response model"""
    id: str
    name: str
    description: Optional[str]
    properties: Dict[str, Dict[str, str]]
    active: bool
    created_at: str
    updated_at: str
    
    model_config = ConfigDict(from_attributes=True)


class SchemaListResponse(BaseModel):
    """List of schemas response"""
    schemas: list[SchemaResponse]
    total: int