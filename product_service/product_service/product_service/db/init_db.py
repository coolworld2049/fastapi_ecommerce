from beanie import init_beanie
from motor import motor_asyncio

from product_service.core.config import settings
from product_service.models.category import Category
from product_service.models.product import Product


async def init_db():
    client = motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URL)
    document_models = [Product, Category]
    await init_beanie(database=client.app, document_models=document_models)
