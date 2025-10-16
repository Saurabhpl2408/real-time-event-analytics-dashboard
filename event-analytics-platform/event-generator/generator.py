import asyncio
import httpx
import random
import os
from datetime import datetime
from faker import Faker
import uuid
import time

fake = Faker()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
EVENTS_PER_SECOND = int(os.getenv("EVENTS_PER_SECOND", "10"))

EVENT_TYPES = ["page_view", "click", "trade", "purchase", "signup"]
SOURCES = ["web", "api", "mobile"]
PAGES = ["/home", "/products", "/about", "/contact", "/checkout", "/profile"]

def generate_event():
    """Generate a random event"""
    event_type = random.choice(EVENT_TYPES)
    
    properties = {}
    if event_type == "page_view":
        properties = {"page": random.choice(PAGES)}
    elif event_type == "click":
        properties = {"button": random.choice(["cta", "menu", "link", "submit"])}
    elif event_type == "trade":
        properties = {
            "symbol": random.choice(["BTC/USD", "ETH/USD", "SOL/USD"]),
            "price": round(random.uniform(100, 50000), 2),
            "volume": round(random.uniform(0.1, 10), 4)
        }
    elif event_type == "purchase":
        properties = {
            "product_id": f"prod_{random.randint(1000, 9999)}",
            "amount": round(random.uniform(10, 500), 2),
            "currency": "USD"
        }
    elif event_type == "signup":
        properties = {
            "plan": random.choice(["free", "basic", "premium"]),
            "referrer": random.choice(["google", "facebook", "direct", "email"])
        }
    
    return {
        "event_id": str(uuid.uuid4()),
        "type": event_type,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "source": random.choice(SOURCES),
        "properties": properties,
        "metadata": {
            "ip": fake.ipv4(),
            "user_agent": fake.user_agent()
        }
    }

async def send_event(client: httpx.AsyncClient, event: dict):
    """Send event to ingestion endpoint"""
    try:
        response = await client.post(f"{BACKEND_URL}/ingest", json=event, timeout=5.0)
        if response.status_code == 200:
            print(f"✓ Sent {event['type']} event (ID: {event['event_id'][:8]}...)")
        else:
            print(f"✗ Failed to send event: {response.status_code}")
    except Exception as e:
        print(f"✗ Error sending event: {e}")

async def main():
    """Main event generation loop"""
    print(f"🚀 Event Generator Started")
    print(f"📡 Backend URL: {BACKEND_URL}")
    print(f"⚡ Rate: {EVENTS_PER_SECOND} events/second")
    print(f"{'='*50}")
    
    # Wait for backend to be ready
    async with httpx.AsyncClient() as client:
        for i in range(30):
            try:
                response = await client.get(f"{BACKEND_URL}/health", timeout=2.0)
                if response.status_code == 200:
                    print("✓ Backend is ready!")
                    break
            except:
                print(f"⏳ Waiting for backend... ({i+1}/30)")
                await asyncio.sleep(2)
        else:
            print("✗ Backend not available, exiting")
            return
    
    # Generate events
    async with httpx.AsyncClient() as client:
        interval = 1.0 / EVENTS_PER_SECOND
        event_count = 0
        start_time = time.time()
        
        while True:
            try:
                event = generate_event()
                await send_event(client, event)
                event_count += 1
                
                # Print stats every 50 events
                if event_count % 50 == 0:
                    elapsed = time.time() - start_time
                    rate = event_count / elapsed
                    print(f"\n📊 Stats: {event_count} events sent | Rate: {rate:.1f} events/sec\n")
                
                await asyncio.sleep(interval)
            
            except KeyboardInterrupt:
                print(f"\n🛑 Generator stopped. Total events sent: {event_count}")
                break
            except Exception as e:
                print(f"Error in main loop: {e}")
                await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())