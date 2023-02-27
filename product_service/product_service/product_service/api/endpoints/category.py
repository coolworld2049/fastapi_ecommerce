from typing import List

from beanie.odm.operators.update.general import Set
from fastapi import APIRouter, HTTPException
from pymongo.results import DeleteResult
from uvicorn.server import logger

from product_service.models.category import (
    Category,
    CategoryCreate,
    CategoryUpdate,
)

router = APIRouter()


@router.get(
    "/",
    response_model=List[Category],
)
async def read_categories(skip: int = 0, limit: int = 10) -> list[Category]:
    category = await Category.find_many(skip=skip, limit=limit).to_list()
    return category


@router.post(
    "/",
    response_model=Category,
)
async def create_category(
    category_in: CategoryCreate,
) -> Category:
    try:
        category = await Category.create(
            Category(**category_in.dict(exclude_unset=True))
        )
        return category
    except Exception as e:
        logger.error(e.args)
        raise HTTPException(status_code=400, detail=e.args)


@router.put(
    "/{name}",
    response_model=Category,
)
async def update_category(
    name: str,
    category_in: CategoryUpdate,
) -> Category | str:
    product = await Category.find_one(Category.name == name)
    if not product:
        raise HTTPException(
            status_code=400, detail="Category with this name doesn`t exist"
        )

    await product.update(Set(category_in.dict()))
    return product


@router.delete(
    "/{name}",
    response_model=dict,
)
async def delete_category(name: str) -> DeleteResult | None:
    category = await Category.find_one(Category.name == name).delete()
    return category
