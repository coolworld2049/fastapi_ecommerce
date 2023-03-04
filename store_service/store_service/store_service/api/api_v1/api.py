from fastapi import APIRouter

from store_service.api.api_v1.endpoints import (
    users,
    products,
    category,
    orders,
    carts,
    login,
    sign_up,
)

api_router = APIRouter()

api_router.include_router(login.router, tags=["login"])
api_router.include_router(sign_up.router, prefix="/sign_up", tags=["sign_up"])
api_router.include_router(users.router, prefix="/users", tags=["user"])
api_router.include_router(category.router, prefix="/categories", tags=["category"])
api_router.include_router(products.router, prefix="/products", tags=["product"])
api_router.include_router(carts.router, prefix="/carts", tags=["cart"])
api_router.include_router(orders.router, prefix="/orders", tags=["order"])
