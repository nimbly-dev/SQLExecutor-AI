from motor.motor_asyncio import AsyncIOMotorClient
from config import settings

class MongoDB:
    def __init__(self):
        self.client = None
        self.db = None

    async def connect(self):
        self.client = AsyncIOMotorClient(settings.mongodb_uri)
        self.db = self.client[settings.MONGO_DB_NAME]
        print(f"Connected to MongoDB database: {settings.MONGO_DB_NAME}")

    async def disconnect(self):
        if self.client:
            self.client.close()
            print("Disconnected from MongoDB")

mongodb = MongoDB()