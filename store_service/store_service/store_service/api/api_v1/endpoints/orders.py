from typing import Optional, Any

from fastapi import APIRouter, Depends
from prisma.enums import OrderStatus
from prisma.models import Order, User
from prisma.partials import OrderWithoutRelations, OrderUpdate
from starlette import status
from starlette.exceptions import HTTPException

from store_service.api.api_v1.deps import params
from store_service.api.api_v1.deps.base import RoleChecker
from store_service.api.api_v1.deps.params import RequestParams
from store_service.api.api_v1.deps.base import get_current_active_user


router = APIRouter()


@router.get(
    "/",
    response_model=list[OrderWithoutRelations],
    dependencies=[Depends(RoleChecker(Order, ["admin", "manager", "customer"]))],
)
async def read_orders(
    request_params: RequestParams = Depends(params.parse_query_params()),
) -> list[Order]:
    order = await Order.prisma().find_many(**request_params.dict(exclude_none=True))
    return order


@router.post(
    "/my",
    response_model=OrderWithoutRelations,
    dependencies=[Depends(RoleChecker(Order, ["admin", "customer"]))],
)
async def create_order(
    cart_id: str,
) -> Optional[Order]:
    order = await Order.prisma().find_unique(where={"cart_id": cart_id})
    if order:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="order with this cart_id already exist",
        )
    order = await Order.prisma().create(
        data={
            "status": OrderStatus.awaiting_payment,
            "cart": {"connect": {"id": cart_id}},
        }
    )
    return order


@router.post(
    "/my/status",
    response_model=OrderStatus,
    dependencies=[Depends(RoleChecker(Order, ["admin", "customer"]))],
)
async def read_order_status(
    current_user: User = Depends(get_current_active_user),
) -> Optional[OrderStatus]:
    user = await User.prisma().find_unique(
        where={"id": current_user.id},
        include={"cart": True},
    )
    order = await Order.prisma().find_unique(where={"cart_id": user.cart.id})
    return order.status


@router.put(
    "/{cart_id}",
    response_model=OrderWithoutRelations,
    dependencies=[Depends(RoleChecker(Order, ["admin"]))],
)
async def update_order(cart_id: str, order_in: OrderUpdate) -> Optional[Order]:
    return await Order.prisma().update(
        where={
            "cart_id": cart_id,
        },
        data=order_in.dict(),
    )


@router.patch(
    "/{cart_id}/status",
    response_model=OrderWithoutRelations,
    dependencies=[Depends(RoleChecker(Order, ["admin", "customer"]))],
)
async def update_order_status(
    cart_id: str, order_status_in: OrderStatus
) -> Optional[Order]:
    return await Order.prisma().update(
        where={
            "cart_id": cart_id,
        },
        data={"status": order_status_in},
    )


@router.delete(
    "/{cart_id}",
    dependencies=[Depends(RoleChecker(Order, ["admin", "customer"]))],
)
async def delete_order(cart_id: str) -> dict[str, Any]:
    await Order.prisma().delete(
        where={
            "cart_id": cart_id,
        }
    )
    return {"status": status.HTTP_200_OK}
