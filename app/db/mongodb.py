from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config.settings import MONGO_URI, MONGO_DB
import asyncio

class MongoDB:
    client: AsyncIOMotorClient = None

mongodb = MongoDB()

async def create_mongodb_connection(retries=10, delay=2):
    for attempt in range(retries):
        try:
            mongodb.client = AsyncIOMotorClient(MONGO_URI)
            print("MongoDB connection created")
            await mongodb.client.admin.command("ping")
            return
        except Exception as e:
            print(f"Cannot connect to mongodb because of {e}")
            await asyncio.sleep(delay)

async def close_mongodb_connection():
    if mongodb.client:
        try:
            mongodb.client.close()
            print("MongoDB connection closed")
        except Exception as e:
            print(f"Cannot close mongodb connection because of {e}")

def get_db() -> AsyncIOMotorDatabase:
    if not mongodb.client:
        raise RuntimeError("MongoDB is not connected")
    return mongodb.client[MONGO_DB]
