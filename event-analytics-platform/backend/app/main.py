from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from aiokafka import AIOKafkaProducer
from redis import asyncio as aioredis
import json
import logging
from typing import Set
from datetime import datetime

from app.schemas import Event, DashboardUpdate
from app.config import settings
from app.utils import setup_logging, serialize_event

# Setup logging
logger = setup_logging()

# FastAPI app
app = FastAPI(title="Real-Time Analytics API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global connections
kafka_producer: AIOKafkaProducer = None
redis_client: aioredis.Redis = None
active_websockets: Set[WebSocket] = set()

@app.on_event("startup")
async def startup_event():
    """Initialize Kafka producer and Redis client"""
    global kafka_producer, redis_client
    
    # Initialize Kafka producer
    kafka_producer = AIOKafkaProducer(
        bootstrap_servers=settings.kafka_bootstrap_servers,
        value_serializer=lambda v: v.encode('utf-8')
    )
    await kafka_producer.start()
    logger.info("Kafka producer started", extra={
        "bootstrap_servers": settings.kafka_bootstrap_servers
    })
    
    # Initialize Redis client
    redis_client = await aioredis.from_url(
        f"redis://{settings.redis_host}:{settings.redis_port}",
        encoding="utf-8",
        decode_responses=True
    )
    logger.info("Redis client connected", extra={
        "host": settings.redis_host,
        "port": settings.redis_port
    })

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup connections"""
    global kafka_producer, redis_client
    
    if kafka_producer:
        await kafka_producer.stop()
        logger.info("Kafka producer stopped")
    
    if redis_client:
        await redis_client.close()
        logger.info("Redis client closed")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "service": "real-time-analytics-api",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    kafka_healthy = kafka_producer is not None
    redis_healthy = redis_client is not None
    
    try:
        await redis_client.ping()
    except:
        redis_healthy = False
    
    return {
        "status": "healthy" if (kafka_healthy and redis_healthy) else "degraded",
        "kafka": "connected" if kafka_healthy else "disconnected",
        "redis": "connected" if redis_healthy else "disconnected",
        "active_connections": len(active_websockets)
    }

@app.post("/ingest")
async def ingest_event(event: Event):
    """
    Ingest a single event
    Validates schema and publishes to Kafka
    """
    try:
        # Serialize event
        event_dict = event.model_dump()
        event_json = serialize_event(event_dict)
        
        # Send to Kafka
        await kafka_producer.send_and_wait(
            settings.kafka_topic,
            value=event_json
        )
        
        logger.info("Event ingested", extra={
            "event_id": event.event_id,
            "event_type": event.type,
            "source": event.source
        })
        
        return {
            "status": "success",
            "event_id": event.event_id,
            "message": "Event ingested successfully"
        }
    
    except Exception as e:
        logger.error("Failed to ingest event", extra={
            "error": str(e),
            "event_id": event.event_id
        })
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time dashboard updates
    Subscribes to Redis pub/sub channel
    """
    await websocket.accept()
    active_websockets.add(websocket)
    
    logger.info("WebSocket client connected", extra={
        "active_connections": len(active_websockets)
    })
    
    # Create Redis pub/sub client
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(settings.redis_pubsub_channel)
    
    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                # Forward message to WebSocket client
                data = message["data"]
                await websocket.send_text(data)
    
    except WebSocketDisconnect:
        active_websockets.remove(websocket)
        await pubsub.unsubscribe(settings.redis_pubsub_channel)
        await pubsub.close()
        logger.info("WebSocket client disconnected", extra={
            "active_connections": len(active_websockets)
        })
    
    except Exception as e:
        logger.error("WebSocket error", extra={"error": str(e)})
        active_websockets.discard(websocket)
        await pubsub.unsubscribe(settings.redis_pubsub_channel)
        await pubsub.close()

@app.get("/stats")
async def get_stats():
    """Get current statistics from Redis"""
    try:
        # Get total event count
        total_events = await redis_client.get("total_events") or 0
        
        # Get events per type
        event_types = await redis_client.hgetall("event_types")
        
        # Get recent minute aggregations
        recent_minutes = []
        keys = await redis_client.keys("agg:*")
        for key in keys[-10:]:  # Last 10 time buckets
            data = await redis_client.hgetall(key)
            if data:
                recent_minutes.append(data)
        
        return {
            "total_events": int(total_events),
            "events_per_type": {k: int(v) for k, v in event_types.items()},
            "recent_aggregations": recent_minutes
        }
    
    except Exception as e:
        logger.error("Failed to fetch stats", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail="Failed to fetch statistics")