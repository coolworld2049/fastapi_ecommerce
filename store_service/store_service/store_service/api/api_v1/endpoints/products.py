from typing import Optional, Any

from fastapi import APIRouter, Depends
from prisma.models import Product, Cart
from prisma.partials import ProductWithoutRelations, ProductCreate, ProductUpdate
from starlette import status

from store_service.api.api_v1.deps import params
from store_service.api.api_v1.deps.base import RoleChecker
from store_service.api.api_v1.deps.params import RequestParams

router = APIRouter()


@router.get(
    "/",
    response_model=list[ProductWithoutRelations],
    dependencies=[
        Depends(RoleChecker(Product, ["admin", "manager", "customer", "guest"]))
    ],
)
async def read_products(
    request_params: RequestParams = Depends(params.parse_query_params()),
) -> list[Product]:
    product = await Product.prisma().find_many(**request_params.dict())
    return product


@router.post(
    "/",
    response_model=ProductWithoutRelations,
    dependencies=[Depends(RoleChecker(Product, ["admin", "manager"]))],
)
async def create_product(product_in: ProductCreate) -> Optional[Product]:
    product = await Product.prisma().create(data=product_in.dict())
    return product


@router.get(
    "/{id}",
    response_model=ProductWithoutRelations,
    dependencies=[Depends(RoleChecker(Product, ["admin", "manager"]))],
)
async def read_product_by_id(
    id: str,
) -> Product | None:
    product = await Product.prisma().find_unique(where={"id": id})
    return product


@router.put(
    "/{id}",
    response_model=ProductWithoutRelations,
    dependencies=[Depends(RoleChecker(Product, ["admin", "manager"]))],
)
async def update_product(id: str, product_in: ProductUpdate) -> Optional[Product]:
    return await Product.prisma().update(
        data=product_in.dict(exclude_unset=True), where={"id": id}
    )


@router.patch(
    "/{id}/product/{category_id}",
    response_model=ProductWithoutRelations,
    dependencies=[Depends(RoleChecker(Product, ["admin", "manager"]))],
)
async def update_product_category(id: str, category_id: str) -> Optional[Product]:
    return await Product.prisma().update(
        data={"category": {"connect": {"id": category_id}}}, where={"id": id}
    )


@router.delete(
    "/{id}",
    dependencies=[Depends(RoleChecker(Product, ["admin", "manager"]))],
)
async def delete_product(id: str) -> dict[str, Any]:
    await Cart.prisma().delete(
        where={
            "id": id,
        }
    )
    await Product.prisma().delete(
        where={
            "id": id,
        },
        include={"category": True, "carts": True},
    )
    return {"status": status.HTTP_200_OK}
