from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from datetime import datetime, timedelta
import csv
import io
from typing import Optional

from app.core.database import get_db
from app.models.users import User
from app.auth.dependencies import get_current_user
from app.models.schemas import Schema

router = APIRouter(prefix="/export", tags=["export"])


@router.get("/csv")
async def export_to_csv(
    schema_id: str = Query(..., description="Schema name to export"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    days: int = Query(7, ge=1, le=90, description="Number of days to export (1-90)"),
    limit: int = Query(10000, ge=1, le=50000, description="Maximum rows (1-50000)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Export events to CSV
    Requires authentication
    """
    try:
        # Verify schema exists
        result = await db.execute(
            select(Schema).where(Schema.name == schema_id)
        )
        schema = result.scalar_one_or_none()
        
        if not schema:
            raise HTTPException(status_code=404, detail=f"Schema '{schema_id}' not found")
        
        # Build query
        time_filter = datetime.utcnow() - timedelta(days=days)
        table_name = f"events_{schema_id}"
        
        # Base query
        query = f"""
        SELECT 
            event_type,
            user_id,
            session_id,
            timestamp,
            properties,
            metadata,
            created_at
        FROM {table_name}
        WHERE timestamp >= :time_filter
        """
        
        # Add event type filter if specified
        if event_type:
            query += " AND event_type = :event_type"
        
        query += " ORDER BY timestamp DESC LIMIT :limit"
        
        # Execute query
        params = {"time_filter": time_filter, "limit": limit}
        if event_type:
            params["event_type"] = event_type
        
        result = await db.execute(text(query), params)
        rows = result.fetchall()
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'event_type',
            'user_id', 
            'session_id',
            'timestamp',
            'properties',
            'metadata',
            'created_at'
        ])
        
        # Write data rows
        for row in rows:
            writer.writerow([
                row[0],  # event_type
                row[1],  # user_id
                row[2],  # session_id
                row[3].isoformat() if row[3] else '',  # timestamp
                str(row[4]) if row[4] else '{}',  # properties (JSON as string)
                str(row[5]) if row[5] else '{}',  # metadata (JSON as string)
                row[6].isoformat() if row[6] else ''   # created_at
            ])
        
        # Prepare response
        output.seek(0)
        
        filename = f"{schema_id}_events_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export data: {str(e)}"
        )


@router.get("/csv/flattened")
async def export_to_csv_flattened(
    schema_id: str = Query(..., description="Schema name to export"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    days: int = Query(7, ge=1, le=90),
    limit: int = Query(10000, ge=1, le=50000),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Export events to CSV with flattened properties
    Each property becomes a separate column
    """
    try:
        # Verify schema
        result = await db.execute(
            select(Schema).where(Schema.name == schema_id)
        )
        schema = result.scalar_one_or_none()
        
        if not schema:
            raise HTTPException(status_code=404, detail=f"Schema '{schema_id}' not found")
        
        # Query events
        time_filter = datetime.utcnow() - timedelta(days=days)
        table_name = f"events_{schema_id}"
        
        query = f"""
        SELECT 
            event_type,
            user_id,
            session_id,
            timestamp,
            properties,
            created_at
        FROM {table_name}
        WHERE timestamp >= :time_filter
        """
        
        if event_type:
            query += " AND event_type = :event_type"
        
        query += " ORDER BY timestamp DESC LIMIT :limit"
        
        params = {"time_filter": time_filter, "limit": limit}
        if event_type:
            params["event_type"] = event_type
        
        result = await db.execute(text(query), params)
        rows = result.fetchall()
        
        # Collect all unique property keys
        all_keys = set()
        for row in rows:
            if row[4]:  # properties
                all_keys.update(row[4].keys())
        
        all_keys = sorted(all_keys)
        
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        header = ['event_type', 'user_id', 'session_id', 'timestamp', 'created_at'] + all_keys
        writer.writerow(header)
        
        # Data rows
        for row in rows:
            base_data = [
                row[0],  # event_type
                row[1],  # user_id
                row[2],  # session_id
                row[3].isoformat() if row[3] else '',  # timestamp
                row[5].isoformat() if row[5] else ''   # created_at
            ]
            
            # Add property values
            properties = row[4] or {}
            property_values = [properties.get(key, '') for key in all_keys]
            
            writer.writerow(base_data + property_values)
        
        output.seek(0)
        
        filename = f"{schema_id}_{event_type or 'all'}_flattened_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export flattened data: {str(e)}"
        )