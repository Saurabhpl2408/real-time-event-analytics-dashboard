from fastapi import FastAPI
from kafka import KafkaConsumer
import os
import json
import threading

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
TOPIC = "health-checks"
app = FastAPI()

consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=KAFKA_BROKER,
    value_deserializer= lambda m: json.loads(m.decode("utf-8")),
    auto_offset_reset = "earliest",
    enable_auto_commit = True,
    group_id = "ping-group"
)

def consume_messages():
    for message in consumer:
        print("Received message", message.value)

threading.Thread(target=consume_messages, daemon=True).start()

@app.get("/ping")
def ping():
    return {"message": "pong"}
