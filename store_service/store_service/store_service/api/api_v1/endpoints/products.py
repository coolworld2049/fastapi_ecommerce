from builtins import str
from typing import Optional, Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Param
from prisma.models import Product, Category
from prisma.partials import (
    ProductWithoutRelations,
    ProductCreate,
    ProductUpdate,
)
from starlette import status

from store_service.api.api_v1.deps import params
from store_service.api.api_v1.deps.auth import RoleChecker
from store_service.api.api_v1.deps.params import RequestParams

router = APIRouter()


@router.get(
    "/",
    response_model=list[Product],
    dependencies=[
        Depends(RoleChecker(["admin", "manager", "customer", "guest"]))
    ],
)
async def read_products(
    request_params: RequestParams = Depends(
        params.parse_query_params(include_example='{"category": false}')
    ),
) -> list[Product]:
    product = await Product.prisma().find_many(
        **request_params.dict(exclude_none=True)
    )
    return product


@router.get(
    "/category",
    response_model=list[ProductWithoutRelations],
    dependencies=[
        Depends(RoleChecker(["admin", "manager", "customer", "guest"]))
    ],
)
async def read_products_by_category(
    name: str = Param(description="category name"),
    request_params: RequestParams = Depends(
        params.parse_query_params(use_order=True)
    ),
) -> list[Product]:
    category = await Category.prisma().find_unique(where={"name": name})
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    where = {"category_id": category.id}
    rp = request_params.dict(exclude_none=True)
    where.update(rp.pop("where")) if rp.get("where") else None
    products = await Product.prisma().find_many(where=where, **rp)
    return products


@router.post(
    "/",
    response_model=ProductWithoutRelations,
    dependencies=[Depends(RoleChecker(["admin", "manager"]))],
)
async def create_product(product_in: ProductCreate) -> Optional[Product]:
    product = await Product.prisma().create(data=product_in.dict())
    return product


@router.get(
    "/{id}",
    response_model=ProductWithoutRelations,
    dependencies=[Depends(RoleChecker(["admin", "manager"]))],
)
async def read_product_by_id(
    id: str,
) -> Product | None:
    product = await Product.prisma().find_unique(where={"id": id})
    return product


@router.put(
    "/{id}",
    response_model=ProductWithoutRelations,
    dependencies=[Depends(RoleChecker(["admin", "manager"]))],
)
async def update_product(
    id: str, product_in: ProductUpdate
) -> Optional[Product]:
    return await Product.prisma().update(
        data=product_in.dict(exclude_unset=True), where={"id": id}
    )


@router.patch(
    "/{id}/category",
    response_model=ProductWithoutRelations,
    dependencies=[Depends(RoleChecker(["admin", "manager"]))],
)
async def update_product_category(
    id: str, category_id: str
) -> Optional[Product]:
    return await Product.prisma().update(
        data={"category": {"connect": {"id": category_id}}}, where={"id": id}
    )


@router.delete(
    "/{id}",
    dependencies=[Depends(RoleChecker(["admin", "manager"]))],
)
async def delete_product(id: str) -> dict[str, Any]:
    product = await Product.prisma().find_unique(where={"id": id})
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    await Product.prisma().delete(
        where={
            "id": id,
        },
        include={"category": True, "orders": True},
    )
    return {"status": status.HTTP_200_OK}
