from typing import Optional, Any

from fastapi import APIRouter, Depends
from prisma.enums import CartStatus
from prisma.models import Cart, User
from prisma.partials import (
    CartWithoutRelations,
)
from starlette import status
from starlette.exceptions import HTTPException

from store_service.api.api_v1.deps import params
from store_service.api.api_v1.deps.base import RoleChecker, get_current_active_user
from store_service.api.api_v1.deps.params import RequestParams
from store_service.core.config import settings
from store_service.validator.cart import CartValidator

router = APIRouter()


@router.get(
    "/",
    tags=["admin", "customer"],
    response_model=list[CartWithoutRelations],
    dependencies=[Depends(RoleChecker(Cart, ["admin", "customer"]))],
)
async def read_carts(
    request_params: RequestParams = Depends(params.parse_query_params()),
) -> list[Cart]:
    cart = await Cart.prisma().find_many(**request_params.dict())
    await CartValidator(cart).is_expire()
    return cart


@router.post(
    "/",
    tags=["admin", "customer"],
    response_model=CartWithoutRelations,
    dependencies=[Depends(RoleChecker(Cart, ["admin", "customer"]))],
)
async def create_cart(user_id: str) -> Optional[Cart]:
    data = {
        "expires_at": settings.cart_expires_timestamp,
        "user": {"connect": {"id": user_id}},
    }
    return await Cart.prisma().create(data=data)


@router.post(
    "/my/create",
    tags=["customer"],
    response_model=CartWithoutRelations,
    dependencies=[Depends(RoleChecker(Cart, ["customer"]))],
)
async def create_cart(
    current_user: User = Depends(get_current_active_user),

) -> Optional[Cart]:
    data = {
        "expires_at": settings.cart_expires_timestamp,
        "user": {"connect": {"id": current_user.id}},
    }
    return await Cart.prisma().create(data=data)


@router.post(
    "/my",
    response_model=CartWithoutRelations,
    dependencies=[Depends(RoleChecker(Cart, ["customer"]))],
)
async def read_my_cart(
    current_user: User = Depends(get_current_active_user),
) -> Optional[Cart]:
    user = await User.prisma().find_unique(
        where={"id": current_user.id},
        include={
            "cart": True
        },
    )
    if not user.cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    await CartValidator(user.cart).is_expire()
    return user.cart


@router.patch(
    "/my/product",
    response_model=CartWithoutRelations,
    dependencies=[Depends(RoleChecker(Cart, ["customer"]))],
)
async def add_products_to_cart(
    product_id: str,
    current_user: User = Depends(get_current_active_user),
) -> Optional[Cart]:
    user = await User.prisma().find_unique(
        where={"id": current_user.id},
        include={
            "cart": True
        },
    )
    ids = [{"id": product_id}]
    data = {"products": {"connect": ids}}
    await CartValidator(user.cart).is_expire()
    return await user.cart.prisma().update(data, where={
        "user_id": current_user.id
    })


@router.delete(
    "/my/product/{product_id}",
    response_model=CartWithoutRelations,
    dependencies=[Depends(RoleChecker(Cart, ["customer"]))],
)
async def delete_product_from_cart(
    product_id: str,
    current_user: User = Depends(get_current_active_user),
) -> Optional[Cart]:
    user = await User.prisma().find_unique(
        where={"id": current_user.id},
        include={
            "cart": True
        },
    )
    ids = [{"id": product_id}]
    data = {"products": {"disconnect": ids}}
    await CartValidator(user.cart).is_expire()
    return await user.cart.prisma().update(data, where={
        "user_id": current_user.id
    })


@router.patch(
    "/{id}/status",
    response_model=CartWithoutRelations,
    dependencies=[Depends(RoleChecker(Cart, ["admin", "customer"]))],
)
async def update_cart_status(id: str, cart_status_in: CartStatus) -> Optional[Cart]:
    cart = await Cart.prisma().update(
        where={
            "id": id,
        },
        data={"status": cart_status_in},
    )
    await CartValidator(cart).is_expire()
    return cart


@router.get(
    "/{id}",
    response_model=CartWithoutRelations,
    dependencies=[Depends(RoleChecker(Cart, ["admin", "customer"]))],
)
async def read_cart_by_id(
    id: str,
) -> Cart | None:
    cart = await Cart.prisma().find_unique(where={"id": id})
    await CartValidator(cart).is_expire()
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
