from fastapi import APIRouter

from product_service.api.endpoints import products, category

api_router = APIRouter()

api_router.include_router(products.router, prefix="/products", tags=["product"])
api_router.include_router(
    category.router, prefix="/categories", tags=["category"]
)
