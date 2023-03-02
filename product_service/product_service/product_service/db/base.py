from motor import motor_asyncio

from product_service.core.config import settings
from product_service.models.cart import Cart
from product_service.models.cart_item import CartItem
from product_service.models.category import Category
from product_service.models.order import Order
from product_service.models.product import Product
from product_service.models.user import User

client = motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URL)
document_models = [
    Cart,
    CartItem,
    Category,
    Order,
    Product,
    User
]
