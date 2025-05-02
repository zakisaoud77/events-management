from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config.settings import MONGO_URI, MONGO_DB

class MongoDB:
    client: AsyncIOMotorClient = None

mongodb = MongoDB()

async def create_mongodb_connection():
    try:
        mongodb.client = AsyncIOMotorClient(MONGO_URI)
        print("MongoDB connection created")
    except Exception as e:
        print(f"Cannot connect to mongodb because of {e}")
        return None

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
