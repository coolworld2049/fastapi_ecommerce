from typing import Optional, Any

from fastapi import APIRouter, Depends
from prisma.enums import OrderStatus
from prisma.models import Order
from prisma.partials import OrderWithoutRelations, OrderUpdate
from starlette import status

from store_service.api.api_v1.deps import params
from store_service.api.api_v1.deps.base import RoleChecker
from store_service.api.api_v1.deps.params import RequestParams

router = APIRouter()


@router.get(
    "/",
    response_model=list[OrderWithoutRelations],
    dependencies=[Depends(RoleChecker(Order, ["admin", "manager", "customer"]))],
)
async def read_orders(
    request_params: RequestParams = Depends(params.parse_query_params()),
) -> list[Order]:
    order = await Order.prisma().find_many(**request_params.dict())
    return order


@router.post(
    "/",
    response_model=OrderWithoutRelations,
    dependencies=[Depends(RoleChecker(Order, ["admin", "customer"]))],
)
async def create_order(cart_id: str) -> Optional[Order]:
    order = await Order.prisma().create(data={"cart": {"connect": {"id": cart_id}}})
    return order


@router.put(
    "/{cart_id}",
    response_model=OrderWithoutRelations,
    dependencies=[Depends(RoleChecker(Order, ["admin", "customer"]))],
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
