from typing import Optional, Any

from fastapi import APIRouter, Depends
from prisma.enums import OrderStatus
from prisma.models import Order, User, Product
from prisma.partials import OrderWithoutRelations, OrderUpdate
from starlette import status
from starlette.exceptions import HTTPException

from store_service.api.api_v1.deps import params
from store_service.api.api_v1.deps.base import RoleChecker, get_current_active_user
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
    order = await Order.prisma().find_many(**request_params.dict(exclude_none=True))
    return order


@router.post(
    "/",
    response_model=OrderWithoutRelations,
    dependencies=[Depends(RoleChecker(Order, ["admin", "customer"]))],
)
async def create_order(
        user_id: str,
) -> Optional[Order]:
    order = await Order.prisma().create(
        data={
            "status": OrderStatus.pending,
            "user": {"connect": {"id": user_id}},
        }
    )
    return order


@router.put(
    "/{user_id}",
    response_model=OrderWithoutRelations,
    dependencies=[Depends(RoleChecker(Order, ["admin"]))],
)
async def update_order(id: str, order_in: OrderUpdate) -> Optional[Order]:
    return await Order.prisma().update(
        where={
            "id": id,
        },
        data=order_in.dict(),
    )


@router.patch(
    "/{user_id}/status",
    response_model=OrderWithoutRelations,
    dependencies=[Depends(RoleChecker(Order, ["admin"]))],
)
async def update_order_status(
        id: str, order_status_in: OrderStatus
) -> Optional[Order]:
    return await Order.prisma().update(
        where={
            "id": id,
        },
        data={"status": order_status_in},
    )


@router.delete(
    "/{user_id}",
    dependencies=[Depends(RoleChecker(Order, ["admin", "customer"]))],
)
async def delete_order(id: str) -> dict[str, Any]:
    await Order.prisma().delete(
        where={
            "id": id,
        }
    )
    return {"status": status.HTTP_200_OK}


@router.patch(
    "/product/{product_id}",
    response_model=OrderWithoutRelations,
    dependencies=[Depends(RoleChecker(Order, ["customer"]))],
)
async def add_products_to_order(
        product_id: str,
        current_user: User = Depends(get_current_active_user),
) -> Optional[Order]:
    user = await User.prisma().find_unique(
        where={"id": current_user.id},
        include={"orders": True},
    )
    order_id = str(*[x.id for x in user.orders if x.status == OrderStatus.pending])
    data = {"products": {"connect": [{"id": product_id}]}}
    return await Order.prisma().update(data=data, where={"id": order_id})


@router.delete(
    "/product/{product_id}",
    response_model=OrderWithoutRelations,
    dependencies=[Depends(RoleChecker(Order, ["customer"]))],
)
async def delete_product_from_order(
        product_id: str,
        current_user: User = Depends(get_current_active_user),
) -> Optional[Order]:
    user = await User.prisma().find_unique(
        where={"id": current_user.id},
        include={"orders": True},
    )
    order_id = str(*[x.id for x in user.orders if x.status == OrderStatus.pending])
    data = {"products": {"disconnect": [{"id": product_id}]}}
    return await Order.prisma().update(data=data, where={"id": order_id})


@router.post(
    "/products/amount",
    response_model=dict,
    dependencies=[Depends(RoleChecker(Order, ["customer"]))],
)
async def my_order_amount(
        current_user: User = Depends(get_current_active_user),
) -> dict:
    user = await User.prisma().find_unique(
        where={"id": current_user.id},
        include={"orders": True},
    )
    order_id = str(*[x.id for x in user.orders if x.status == OrderStatus.pending])
    order = await Order.prisma().find_unique(where={"id": order_id}, include={"products": True})
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return {"amount": sum([x.price for x in order.products])}
