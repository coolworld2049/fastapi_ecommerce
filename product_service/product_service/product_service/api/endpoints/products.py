from typing import List, Optional

from beanie.odm.operators.update.general import Set
from fastapi import APIRouter, HTTPException
from pymongo.results import DeleteResult
from uvicorn.server import logger

from product_service.models.category import Category
from product_service.models.product import Product, ProductCreate, ProductUpdate

router = APIRouter()


@router.get(
    "/",
    response_model=List[Product],
)
async def read_products(skip: int = 0, limit: int = 10) -> list[Product]:
    products = await Product.find_many(skip=skip, limit=limit).to_list()
    return products


@router.post(
    "/",
    response_model=Product,
)
async def create_product(
    product_in: ProductCreate,
) -> Product:
    category = await Category.find_one(
        Category.name == product_in.category_name
    )
    if not category:
        raise HTTPException(
            status_code=400, detail="Category with this name doesn`t exist"
        )
    try:
        product = await Product.create(
            Product(**product_in.dict(exclude_unset=True))
        )
        return product
    except Exception as e:
        logger.error(e.args)
        raise HTTPException(status_code=400, detail=e.args)


@router.put(
    "/{product_title}",
    response_model=Product,
)
async def update_product(
    product_title: str,
    product_in: ProductUpdate,
) -> Optional[Product]:
    product = await Product.find_one(Product.title == product_title)
    if product:
        raise HTTPException(
            status_code=400, detail="Product with this title doesn`t exist"
        )

    await product.update(Set(product_in.dict()))
    return product


@router.delete(
    "/{product_title}",
    response_model=dict,
)
async def delete_product(product_title: str) -> DeleteResult | None:
    product = await Product.find_one(Product.title == product_title).delete()
    return product
