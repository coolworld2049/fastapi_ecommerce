from fastapi import APIRouter

from order_service.api.api_v1.endpoints import (
    login,
    signup,
    orders,
    carts,
    cart_items,
)
from order_service.api.api_v1.endpoints import users
from order_service.api.api_v1.endpoints import utils

api_router = APIRouter()

api_router.include_router(login.router, tags=["login"])
api_router.include_router(signup.router, tags=["signup"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(orders.router, prefix="/orders", tags=["order"])
api_router.include_router(carts.router, prefix="/carts", tags=["cart"])
api_router.include_router(
    cart_items.router, prefix="/cart_items", tags=["cart_item"]
)
