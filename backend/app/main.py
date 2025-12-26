from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select as sql_select
from contextlib import asynccontextmanager
from datetime import datetime
import logging
import json
import os

from app.config import settings, CORS_ORIGINS
from app.core.database import init_db, get_db
from app.core.kafka_producer import kafka_producer
from app.api import schemas, adaptors, events

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events"""
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    
    # Initialize database
    await init_db()
    
    # Start Kafka producer
    await kafka_producer.start()
    
    logger.info("✅ All services started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    await kafka_producer.stop()
    logger.info("✅ Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Schema-driven, multi-adaptor analytics platform with Grafana visualization",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# BASIC ENDPOINTS
# ============================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "environment": settings.environment,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version
    }


# ============================================
# TAG MANAGER ENDPOINTS
# ============================================

async def build_tag_script(adaptor) -> str:
    """
    Build the complete tag manager script
    """
    
    tag_manager_dir = "/app/tag-manager"
    
    # Read core tracker
    tracker_path = os.path.join(tag_manager_dir, "core", "tracker.js")
    try:
        with open(tracker_path, 'r') as f:
            core_tracker = f.read()
    except FileNotFoundError:
        core_tracker = "// Core tracker not found\nconsole.error('[Analytics] Core tracker missing');"
    
    # Read container template
    container_template_path = os.path.join(tag_manager_dir, "core", "container-template.js")
    try:
        with open(container_template_path, 'r') as f:
            container_template = f.read()
    except FileNotFoundError:
        container_template = "// Container template not found\nconsole.error('[Analytics] Container template missing');"
    
    # Get custom adaptor code
    custom_code = ""
    if adaptor.custom_code:
        custom_code = adaptor.custom_code
    else:
        adaptor_file = f"{adaptor.schema_id}-adaptor.js"
        adaptor_path = os.path.join(tag_manager_dir, "adaptors", adaptor_file)
        
        if os.path.exists(adaptor_path):
            with open(adaptor_path, 'r') as f:
                custom_code = f.read()
    
    # Replace placeholders (FIXED - no extra quotes)
    container_code = container_template.replace(
        '"PLACEHOLDER_CONTAINER_ID"',  # CHANGED: Added quotes in placeholder
        f'"{adaptor.container_id}"'
    ).replace(
        '"PLACEHOLDER_SCHEMA_ID"',     # CHANGED: Added quotes in placeholder
        f'"{adaptor.schema_id}"'
    ).replace(
        '"PLACEHOLDER_API_URL"',       # CHANGED: Added quotes in placeholder
        f'"{settings.tag_manager_base_url}"'
    ).replace(
        'PLACEHOLDER_TRACKING_RULES',  # This is fine (no quotes needed)
        json.dumps(adaptor.tracking_rules)
    ).replace(
        'PLACEHOLDER_DEBUG',           # This is fine (no quotes needed)
        'true' if settings.environment == 'development' else 'false'
    ).replace(
        'PLACEHOLDER_CUSTOM_CODE',
        custom_code
    )
    
    # Combine all parts
    full_script = f"""/**
 * Custom Analytics Platform - Tag Manager
 * Container ID: {adaptor.container_id}
 * Schema: {adaptor.schema_id}
 * Generated: {datetime.utcnow().isoformat()}
 */

{core_tracker}

{container_code}
"""
    
    return full_script


@app.get("/tag/{container_id}.js")
async def serve_tag_script(
    container_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Serve dynamically generated tag manager script
    """
    try:
        from app.models.adaptors import Adaptor
        
        result = await db.execute(
            sql_select(Adaptor).where(Adaptor.container_id == container_id)
        )
        adaptor = result.scalar_one_or_none()
        
        if not adaptor:
            raise HTTPException(status_code=404, detail=f"Container '{container_id}' not found")
        
        if not adaptor.active:
            raise HTTPException(status_code=403, detail=f"Container '{container_id}' is inactive")
        
        # Build the script
        script_content = await build_tag_script(adaptor)
        
        return Response(
            content=script_content,
            media_type="application/javascript",
            headers={
                "Cache-Control": "public, max-age=300",
                "Access-Control-Allow-Origin": "*"
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to serve tag script: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate tag script")


@app.options("/tag/{container_id}.js")
async def tag_options(container_id: str):
    """Handle CORS preflight for tag scripts"""
    return Response(
        content="",
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "*"
        }
    )


# ============================================
# INCLUDE API ROUTERS
# ============================================

app.include_router(schemas.router, prefix="/api")
app.include_router(adaptors.router, prefix="/api")
app.include_router(events.router, prefix="/api")