from fastapi import APIRouter

from product_service.api.endpoints import products, category, cart_items, carts, orders, users, login, signup

api_router = APIRouter()


api_router.include_router(login.router, tags=["login"])
api_router.include_router(signup.router, tags=["signup"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(products.router, prefix="/products", tags=["product"])
api_router.include_router(
    category.router, prefix="/categories", tags=["category"]
)
api_router.include_router(orders.router, prefix="/orders", tags=["order"])
api_router.include_router(carts.router, prefix="/carts", tags=["carts"])
api_router.include_router(
    cart_items.router, prefix="/cart_items", tags=["cart_item"]
)
