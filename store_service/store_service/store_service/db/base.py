import motor.motor_asyncio
from pymongo.database import Database

from store_service.core.config import settings

client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URL)

dbapp: Database = client.app

