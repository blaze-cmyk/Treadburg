import asyncio
import sys
import os

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import init_db
from core.ingestion.watcher import watcher
from core.ingestion.pipeline import pipeline

async def main():
    print("🚀 Starting TradeBerg Event-Driven Ingestion System...")
    
    # 1. Initialize DB (Ensure tables exist)
    init_db()
    
    # 2. Run Watcher and Worker concurrently
    # In a real system, these would be separate services/containers.
    # Here we run them in the same event loop for simulation.
    
    try:
        await asyncio.gather(
            watcher.start(poll_interval=60),  # Poll RSS every 60s
            pipeline.start(poll_interval=5)   # Poll Queue every 5s
        )
    except KeyboardInterrupt:
        print("\n🛑 Stopping Ingestion System...")

if __name__ == "__main__":
    asyncio.run(main())
