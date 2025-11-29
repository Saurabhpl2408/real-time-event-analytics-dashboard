from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.adaptors import Adaptor
from app.models.schemas import Schema
from app.schemas_pydantic import (
    AdaptorCreate,
    AdaptorUpdate,
    AdaptorResponse,
    AdaptorListResponse,
    ContainerCodeResponse
)
from app.config import settings

router = APIRouter(prefix="/adaptors", tags=["adaptors"])


@router.post("/", response_model=AdaptorResponse, status_code=201)
async def create_adaptor(
    adaptor_data: AdaptorCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new tracking adaptor"""
    try:
        # Verify schema exists
        result = await db.execute(
            select(Schema).where(Schema.name == adaptor_data.schema_id)
        )
        schema = result.scalar_one_or_none()
        
        if not schema:
            raise HTTPException(status_code=404, detail=f"Schema '{adaptor_data.schema_id}' not found")
        
        # Create adaptor
        adaptor = Adaptor(
            name=adaptor_data.name,
            description=adaptor_data.description,
            schema_id=adaptor_data.schema_id,
            website_url=adaptor_data.website_url,
            allowed_domains=adaptor_data.allowed_domains,
            tracking_rules=adaptor_data.tracking_rules,
            custom_code=adaptor_data.custom_code
        )
        
        # Generate container ID
        adaptor.container_id = adaptor.generate_container_id()
        
        db.add(adaptor)
        await db.commit()
        await db.refresh(adaptor)
        
        return AdaptorResponse(**adaptor.to_dict())
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create adaptor: {str(e)}")


@router.get("/", response_model=AdaptorListResponse)
async def list_adaptors(
    skip: int = 0,
    limit: int = 100,
    schema_id: str = None,
    active_only: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """List all adaptors"""
    try:
        query = select(Adaptor)
        
        if schema_id:
            query = query.where(Adaptor.schema_id == schema_id)
        if active_only:
            query = query.where(Adaptor.active == True)
        
        # Get total
        count_result = await db.execute(query)
        total = len(count_result.scalars().all())
        
        # Get adaptors
        result = await db.execute(
            query.offset(skip).limit(limit).order_by(Adaptor.created_at.desc())
        )
        adaptors = result.scalars().all()
        
        return AdaptorListResponse(
            adaptors=[AdaptorResponse(**a.to_dict()) for a in adaptors],
            total=total
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list adaptors: {str(e)}")


@router.get("/{container_id}", response_model=AdaptorResponse)
async def get_adaptor(
    container_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get adaptor by container ID"""
    try:
        result = await db.execute(
            select(Adaptor).where(Adaptor.container_id == container_id)
        )
        adaptor = result.scalar_one_or_none()
        
        if not adaptor:
            raise HTTPException(status_code=404, detail=f"Adaptor '{container_id}' not found")
        
        return AdaptorResponse(**adaptor.to_dict())
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get adaptor: {str(e)}")


@router.get("/{container_id}/code", response_model=ContainerCodeResponse)
async def get_container_code(
    container_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get installation code for container"""
    try:
        result = await db.execute(
            select(Adaptor).where(Adaptor.container_id == container_id)
        )
        adaptor = result.scalar_one_or_none()
        
        if not adaptor:
            raise HTTPException(status_code=404, detail=f"Container '{container_id}' not found")
        
        script_url = f"{settings.tag_manager_base_url}/tag/{container_id}.js"
        installation_code = f'<script src="{script_url}" async></script>'
        
        return ContainerCodeResponse(
            container_id=container_id,
            script_url=script_url,
            installation_code=installation_code
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get code: {str(e)}")


@router.put("/{container_id}", response_model=AdaptorResponse)
async def update_adaptor(
    container_id: str,
    adaptor_data: AdaptorUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update adaptor"""
    try:
        result = await db.execute(
            select(Adaptor).where(Adaptor.container_id == container_id)
        )
        adaptor = result.scalar_one_or_none()
        
        if not adaptor:
            raise HTTPException(status_code=404, detail=f"Adaptor '{container_id}' not found")
        
        # Update fields
        update_data = adaptor_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(adaptor, field, value)
        
        await db.commit()
        await db.refresh(adaptor)
        
        return AdaptorResponse(**adaptor.to_dict())
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update adaptor: {str(e)}")


@router.delete("/{container_id}")
async def delete_adaptor(
    container_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete adaptor (soft delete)"""
    try:
        result = await db.execute(
            select(Adaptor).where(Adaptor.container_id == container_id)
        )
        adaptor = result.scalar_one_or_none()
        
        if not adaptor:
            raise HTTPException(status_code=404, detail=f"Adaptor '{container_id}' not found")
        
        adaptor.active = False
        await db.commit()
        
        return {"status": "success", "message": f"Adaptor '{container_id}' deactivated"}
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete adaptor: {str(e)}")