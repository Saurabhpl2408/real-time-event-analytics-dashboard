from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update as sql_update, delete as sql_delete
from typing import List

from app.core.database import get_db
from app.core.schema_engine import SchemaEngine
from app.models.schemas import Schema
from app.schemas_pydantic import (
    SchemaCreate,
    SchemaUpdate,
    SchemaResponse,
    SchemaListResponse
)

router = APIRouter(prefix="/schemas", tags=["schemas"], redirect_slashes=True)


@router.post("/", response_model=SchemaResponse, status_code=201)
async def create_schema(
    schema_data: SchemaCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new schema definition"""
    try:
        # Check if schema with same name exists
        result = await db.execute(
            select(Schema).where(Schema.name == schema_data.name)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            raise HTTPException(status_code=400, detail=f"Schema '{schema_data.name}' already exists")
        
        # Create schema
        schema = Schema(
            name=schema_data.name,
            description=schema_data.description,
            properties=schema_data.properties
        )
        
        db.add(schema)
        await db.commit()
        await db.refresh(schema)
        
        # Create database table for this schema
        await SchemaEngine.create_event_table(db, schema.name, schema.properties)
        
        return SchemaResponse(**schema.to_dict())
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create schema: {str(e)}")


@router.get("/", response_model=SchemaListResponse)
async def list_schemas(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """List all schemas"""
    try:
        # Build query
        query = select(Schema)
        if active_only:
            query = query.where(Schema.active == True)
        
        # Get total count
        count_result = await db.execute(query)
        total = len(count_result.scalars().all())
        
        # Get schemas with pagination
        result = await db.execute(
            query.offset(skip).limit(limit).order_by(Schema.created_at.desc())
        )
        schemas = result.scalars().all()
        
        return SchemaListResponse(
            schemas=[SchemaResponse(**s.to_dict()) for s in schemas],
            total=total
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list schemas: {str(e)}")


@router.get("/{schema_name}", response_model=SchemaResponse)
async def get_schema(
    schema_name: str,
    db: AsyncSession = Depends(get_db)
):
    """Get schema by name"""
    try:
        result = await db.execute(
            select(Schema).where(Schema.name == schema_name)
        )
        schema = result.scalar_one_or_none()
        
        if not schema:
            raise HTTPException(status_code=404, detail=f"Schema '{schema_name}' not found")
        
        return SchemaResponse(**schema.to_dict())
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get schema: {str(e)}")


@router.put("/{schema_name}", response_model=SchemaResponse)
async def update_schema(
    schema_name: str,
    schema_data: SchemaUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update schema"""
    try:
        # Find schema
        result = await db.execute(
            select(Schema).where(Schema.name == schema_name)
        )
        schema = result.scalar_one_or_none()
        
        if not schema:
            raise HTTPException(status_code=404, detail=f"Schema '{schema_name}' not found")
        
        # Update fields
        update_data = schema_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(schema, field, value)
        
        await db.commit()
        await db.refresh(schema)
        
        return SchemaResponse(**schema.to_dict())
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update schema: {str(e)}")


@router.delete("/{schema_name}")
async def delete_schema(
    schema_name: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete schema (soft delete - marks as inactive)"""
    try:
        result = await db.execute(
            select(Schema).where(Schema.name == schema_name)
        )
        schema = result.scalar_one_or_none()
        
        if not schema:
            raise HTTPException(status_code=404, detail=f"Schema '{schema_name}' not found")
        
        # Soft delete - mark as inactive
        schema.active = False
        await db.commit()
        
        return {"status": "success", "message": f"Schema '{schema_name}' deactivated"}
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete schema: {str(e)}")