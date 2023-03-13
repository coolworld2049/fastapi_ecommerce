import motor.motor_asyncio
from pymongo.database import Database

from store_service.core.config import get_app_settings

client = motor.motor_asyncio.AsyncIOMotorClient(get_app_settings().MONGODB_URL)

dbapp: Database = client.app
