from fastapi import FastAPI
from kafka import KafkaProducer
import os
import json

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
TOPIC = "health-checks"

app = FastAPI()

producer = KafkaProducer(
    bootstrap_servers = KAFKA_BROKER,
    value_serializer = lambda v:json.dumps(v).encode("utf-8")
)

@app.get("/health")
def health ():
    message =  { "status": "ok"}
    producer.send(TOPIC, message)
    producer.flush()
    return message