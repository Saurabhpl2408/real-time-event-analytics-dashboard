from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
import os
import uuid
from datetime import datetime
from typing import List
import time

from models import (
    EventRequest, BatchEventRequest, EnrichedEvent, 
    EventResponse, BatchEventResponse
)
from database import (
    test_database_connection, get_database_stats, 
    get_recent_events, create_tables_if_not_exist
)
from kafka_client import get_publisher

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Event Ingestion Service",
    description="Real-time event ingestion API for analytics platform",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc"  # ReDoc
)

# Add CORS middleware for web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for monitoring
startup_time = datetime.utcnow()
request_count = 0
error_count = 0

def enrich_event(event_request: EventRequest, request: Request) -> EnrichedEvent:
    """Enrich event with metadata"""
    current_time = datetime.utcnow()
    
    # Generate unique event ID
    event_id = str(uuid.uuid4())
    
    # Extract client information
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    
    # Create enriched event
    enriched = EnrichedEvent(
        event_id=event_id,
        event_type=event_request.event_type.value,
        source=event_request.source.value,
        user_id=event_request.user_id,
        session_id=event_request.session_id,
        timestamp=current_time,
        properties=event_request.properties,
        context={
            **event_request.context,  # Original context
            # Add ingestion metadata
            "ingestion": {
                "service": "event-ingestion",
                "version": "1.0.0",
                "client_ip": client_ip,
                "user_agent": user_agent
            }
        },
        ingestion_timestamp=current_time,
        ingestion_metadata={
            "service_name": "event-ingestion",
            "ingestion_latency_ms": 0,  # Will be calculated
            "request_id": str(uuid.uuid4())
        }
    )
    
    return enriched

@app.on_event("startup")
async def startup_event():
    """Initialize service on startup"""
    try:
        logger.info("Starting Event Ingestion Service...")
        
        # Test database connection
        db_connected, db_info = test_database_connection()
        if not db_connected:
            logger.error(f"Database connection failed: {db_info}")
            # Don't fail startup - allow graceful degradation
        else:
            logger.info("Database connection successful")
            # Ensure tables exist
            create_tables_if_not_exist()
        
        # Test Kafka connection
        publisher = get_publisher()
        kafka_connected, kafka_info = publisher.test_kafka_connection()
        if not kafka_connected:
            logger.error(f"Kafka connection failed: {kafka_info}")
            # Don't fail startup - allow graceful degradation
        else:
            logger.info("Kafka connection successful")
        
        logger.info("Event Ingestion Service started successfully")
        
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        # In production, you might want to exit here
        # raise e

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    try:
        logger.info("Shutting down Event Ingestion Service...")
        publisher = get_publisher()
        publisher.close()
        logger.info("Shutdown complete")
    except Exception as e:
        logger.error(f"Shutdown error: {e}")

@app.middleware("http")
async def track_requests(request: Request, call_next):
    """Middleware to track requests and response times"""
    global request_count, error_count
    
    start_time = time.time()
    request_count += 1
    
    try:
        response = await call_next(request)
        
        # Log request details
        process_time = time.time() - start_time
        logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")
        
        # Add response headers
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Request-ID"] = str(request_count)
        
        return response
        
    except Exception as e:
        error_count += 1
        logger.error(f"Request failed: {e}")
        raise

@app.post("/events", response_model=EventResponse)
async def ingest_single_event(
    event: EventRequest, 
    request: Request,
    background_tasks: BackgroundTasks
):
    """Ingest a single event"""
    try:
        start_time = time.time()
        
        # Enrich the event
        enriched_event = enrich_event(event, request)
        
        # Calculate ingestion latency
        enriched_event.ingestion_metadata["ingestion_latency_ms"] = (time.time() - start_time) * 1000
        
        # Publish to Kafka
        publisher = get_publisher()
        publish_result = publisher.publish_event(enriched_event.dict())
        
        logger.info(f"Event {enriched_event.event_id} ingested successfully")
        
        return EventResponse(
            status="success",
            event_id=enriched_event.event_id,
            timestamp=enriched_event.timestamp,
            message="Event ingested successfully"
        )
        
    except Exception as e:
        logger.error(f"Failed to ingest event: {e}")
        raise HTTPException(status_code=500, detail=f"Event ingestion failed: {str(e)}")

@app.post("/events/batch", response_model=BatchEventResponse)
async def ingest_batch_events(
    batch: BatchEventRequest,
    request: Request
):
    """Ingest multiple events in batch"""
    try:
        start_time = time.time()
        
        enriched_events = []
        event_ids = []
        
        # Enrich all events
        for event_request in batch.events:
            enriched = enrich_event(event_request, request)
            enriched_events.append(enriched.dict())
            event_ids.append(enriched.event_id)
        
        # Batch publish to Kafka
        publisher = get_publisher()
        publish_result = publisher.publish_batch(enriched_events)
        
        total_time = (time.time() - start_time) * 1000
        
        logger.info(f"Batch ingested: {publish_result['success_count']} successful, {publish_result['failure_count']} failed in {total_time:.2f}ms")
        
        return BatchEventResponse(
            status="completed",
            total_events=len(batch.events),
            successful=publish_result['success_count'],
            failed=publish_result['failure_count'],
            event_ids=event_ids,
            errors=[f["error"] for f in publish_result['failed']] if publish_result['failed'] else []
        )
        
    except Exception as e:
        logger.error(f"Failed to ingest batch: {e}")
        raise HTTPException(status_code=500, detail=f"Batch ingestion failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        db_connected, db_info = test_database_connection()
        publisher = get_publisher()
        kafka_connected, kafka_info = publisher.test_kafka_connection()
        uptime_seconds = (datetime.utcnow() - startup_time).total_seconds()
        
        health_status = {
            "status": "healthy" if db_connected and kafka_connected else "degraded",
            "service": "event-ingestion",
            "version": "1.0.0",
            "uptime_seconds": uptime_seconds,
            "timestamp": datetime.utcnow().isoformat(),
            "dependencies": {
                "database": {
                    "status": "connected" if db_connected else "disconnected",
                    "info": db_info
                },
                "kafka": {
                    "status": "connected" if kafka_connected else "disconnected", 
                    "info": kafka_info
                }
            },
            "metrics": {
                "total_requests": request_count,
                "total_errors": error_count,
                "error_rate": error_count / max(request_count, 1) * 100
            }
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")

@app.get("/stats")
async def get_stats():
    """Get service statistics"""
    try:
        db_stats = get_database_stats()
        recent = get_recent_events(5)
        publisher = get_publisher()
        topic_info = publisher.get_topic_info()
        
        return {
            "service": "event-ingestion",
            "uptime_seconds": (datetime.utcnow() - startup_time).total_seconds(),
            "database_stats": db_stats,
            "recent_events": recent,
            "kafka_info": topic_info,
            "request_metrics": {
                "total_requests": request_count,
                "total_errors": error_count
            }
        }
        
    except Exception as e:
        logger.error(f"Stats endpoint failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to get stats")

@app.get("/")
async def root():
    """Root endpoint with service info"""
    return {
        "service": "Event Ingestion Service",
        "version": "1.0.0",
        "description": "Real-time event ingestion API for analytics platform",
        "endpoints": {
            "health": "/health",
            "stats": "/stats",
            "single_event": "POST /events",
            "batch_events": "POST /events/batch",
            "documentation": "/docs"
        },
        "uptime_seconds": (datetime.utcnow() - startup_time).total_seconds()
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        reload=True,  
        log_level="info"
    )