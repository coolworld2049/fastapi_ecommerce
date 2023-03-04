from typing import Optional, Any

from fastapi import APIRouter, Depends
from prisma.enums import CartStatus
from prisma.models import Cart, User
from prisma.partials import (
    CartWithoutRelations,
    CartProductInput,
)
from starlette import status

from store_service.api.api_v1.deps import params
from store_service.api.api_v1.deps.base import RoleChecker, get_current_active_user
from store_service.api.api_v1.deps.params import RequestParams
from store_service.core.config import settings

router = APIRouter()


@router.get(
    "/",
    response_model=list[CartWithoutRelations],
    dependencies=[Depends(RoleChecker(Cart, ["admin", "customer"]))],
)
async def read_carts(
    request_params: RequestParams = Depends(params.parse_query_params()),
) -> list[Cart]:
    cart = await Cart.prisma().find_many(**request_params.dict())
    return cart


@router.post(
    "/",
    response_model=CartWithoutRelations,
    dependencies=[Depends(RoleChecker(Cart, ["admin", "customer"]))],
)
async def create_cart(user_id: str) -> Optional[Cart]:
    data = {
        "expires_at": settings.cart_expires_timestamp,
        "user": {"connect": {"id": user_id}},
    }

    return await Cart.prisma().create(data=data)


@router.get(
    "/{id}",
    response_model=CartWithoutRelations,
    dependencies=[Depends(RoleChecker(Cart, ["admin", "customer"]))],
)
async def read_cart_by_id(
    id: str,
) -> Cart | None:
    cart = await Cart.prisma().find_unique(where={"id": id})
    return cart


@router.patch(
    "/{id}/status",
    response_model=CartWithoutRelations,
    dependencies=[Depends(RoleChecker(Cart, ["admin", "customer"]))],
)
async def update_cart_status(id: str, cart_status_in: CartStatus) -> Optional[Cart]:
    return await Cart.prisma().update(
        where={
            "id": id,
        },
        data={"status": cart_status_in},
    )


@router.patch(
    "/{id}/product",
    response_model=CartWithoutRelations,
    dependencies=[Depends(RoleChecker(Cart, ["customer"]))],
)
async def add_products_to_cart(
    id: str,
    product_ids: CartProductInput,
) -> Optional[Cart]:
    ids = [{"id": x} for x in product_ids.product_ids]
    data = {"products": {"set": ids, "connect": ids}}
    cart = await Cart.prisma().update(data=data, where={"id": id})
    return cart


@router.get(
    "/cost",
    response_model=CartWithoutRelations,
    dependencies=[Depends(RoleChecker(Cart, ["customer"]))],
)
async def read_my_cart_cost(
    current_user: User = Depends(get_current_active_user),
) -> Optional[Cart]:
    cart = await User.prisma().find_unique(
        where={"id": current_user.id},
        include={
            "carts": {
                "where": {"user_id": current_user.id, "status": CartStatus.active.name}
            }
        },
    )
    return cart


@router.patch(
    "/{id}/product/{product_id}",
    response_model=CartWithoutRelations,
    dependencies=[Depends(RoleChecker(Cart, ["admin", "customer"]))],
)
async def delete_product_from_cart(
    id: str,
    product_id: str,
) -> Optional[Cart]:
    data = {"products": {"disconnect": [{"id": product_id}]}}
    cart = await Cart.prisma().update(data=data, where={"id": id})
    return cart


@router.delete(
    "/{id}",
    dependencies=[Depends(RoleChecker(Cart, ["admin", "customer"]))],
)
async def delete_cart(id: str) -> dict[str, Any]:
    await Cart.prisma().delete(
        where={
            "id": id,
        },
        include={"products": True},
    )
    return {"status": status.HTTP_200_OK}
