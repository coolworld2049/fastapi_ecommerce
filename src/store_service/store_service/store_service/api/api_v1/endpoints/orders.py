from builtins import str
from typing import Optional, Any

from fastapi import APIRouter, Depends
from prisma.enums import OrderStatus
from prisma.models import Order, Product, OrderProduct
from prisma.partials import OrderWithoutRelations
from prisma.types import OrderInclude
from starlette import status
from starlette.exceptions import HTTPException

from store_service.api.api_v1.deps import params
from store_service.api.api_v1.deps.auth import (
    RoleChecker,
    get_current_active_user,
)
from store_service.core.config import get_app_settings
from store_service.core.settings.base import AppEnvTypes
from store_service.schemas.request_params import RequestParams
from store_service.schemas.user import User

router = APIRouter()


async def get_current_user_order(
    current_user: User,
    include: Optional[OrderInclude] = None,
    order_status: OrderStatus = OrderStatus.pending,
) -> Order | None:
    current_user_orders = await Order.prisma().find_many(
        where={"user_id": {"equals": current_user.id}}
    )
    order = list(
        filter(lambda x: x.status == order_status, current_user_orders)
    )
    if not len(order) > 0:
        return None
    order = order[0]
    order = await Order.prisma().find_unique(
        where={"id": order.id}, include=include
    )
    return order


@router.get(
    "/",
    response_model=list[Order | OrderWithoutRelations],
    dependencies=None
    if get_app_settings().APP_ENV == AppEnvTypes.test
    else [Depends(RoleChecker(["admin"]))],
)
async def read_all_orders(
    request_params: RequestParams = Depends(
        params.parse_query_params(include_example='{"order_products": false}')
    ),
) -> list[Order]:
    order = await Order.prisma().find_many(
        **request_params.dict(exclude_none=True)
    )
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return order


@router.get(
    "/me",
    response_model=Order,
    dependencies=[Depends(RoleChecker(["admin", "customer"]))],
)
async def read_order_me(
    current_user: User = Depends(get_current_active_user),
) -> Optional[Order]:
    order = await get_current_user_order(
        current_user, include={"order_products": True}
    )
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return order


@router.post(
    "/",
    response_model=OrderWithoutRelations,
    dependencies=[Depends(RoleChecker(["admin", "customer"]))],
)
async def create_order(
    current_user: User = Depends(get_current_active_user),
) -> Optional[Order]:
    order = await Order.prisma().create(
        data={
            "status": OrderStatus.pending,
            "cost": 0.0,
            "user_id": current_user.id,
        },
        include={"order_products": True},
    )
    return order


@router.patch(
    "/product/add",
    response_model=OrderWithoutRelations,
    dependencies=[Depends(RoleChecker(["admin", "customer"]))],
)
async def add_products_to_order(
    product_id: str,
    current_user: User = Depends(get_current_active_user),
) -> Optional[Order]:
    product = await Product.prisma().find_unique(where={"id": product_id})
    order = await get_current_user_order(current_user)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    order = await order.prisma().update(
        data={
            "cost": {"increment": float(product.price)},
            "order_products": {
                "create": [
                    {
                        "product_id": product_id,
                    }
                ],
            },
        },
        where={"id": order.id},
        include={"order_products": True},
    )
    await OrderProduct.prisma().update(
        data={"product": {"connect": {"id": product_id}}},
        where={"id": order.id},
    )
    await product.prisma().update(
        data={"stock": {"decrement": 1}},
        where={"id": product.id},
    )
    return order


@router.patch(
    "/product/delete",
    response_model=OrderWithoutRelations,
    dependencies=[Depends(RoleChecker(["admin", "customer"]))],
)
async def delete_product_from_order(
    product_id: str,
    current_user: User = Depends(get_current_active_user),
) -> Optional[Order]:
    product = await Product.prisma().find_unique(where={"id": product_id})
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    order = await get_current_user_order(
        current_user, include={"order_products": True}
    )
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    order_products_where_product_id = list(
        filter(lambda x: x.product_id == product.id, order.order_products)
    )
    if not order_products_where_product_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    order_products_without_product_id = list(
        filter(lambda x: x.product_id != product.id, order.order_products)
    )
    order = await order.prisma().update(
        data={
            "cost": {
                "decrement": float(product.price)
                * len(order_products_where_product_id)
            },
            "order_products": {
                "delete": [
                    {
                        "id": x.id,
                    }
                    for x in order_products_where_product_id
                ]
            },
        },
        where={"id": order.id},
        include={"order_products": True},
    )
    await OrderProduct.prisma().update(
        data={"product": {"disconnect": True}}, where={"id": order.id}
    )
    product = await Product.prisma().update_many(
        data={"stock": {"decrement": 1}},
        where={
            "id": {"in": [x.id for x in order_products_without_product_id]}
        },
    )
    return order


@router.delete(
    "/me",
    dependencies=[Depends(RoleChecker(["admin", "customer"]))],
)
async def delete_order_me(
    current_user: User = Depends(get_current_active_user),
) -> dict[str, Any]:
    order = await get_current_user_order(current_user)
    if not order:
        raise HTTPException(status_code=status.HTTP_200_OK)
    data = {"status": OrderStatus.deleted}
    order_product_ids = (
        list(map(lambda x: x.id, order.order_products))
        if order.order_products
        else None
    )
    if order_product_ids:
        data.update(
            {
                "order_products": {
                    "disconnect": {"id": x} for x in order_product_ids
                }
            }
        )
    await order.prisma().update(
        data=data,
        where={"id": order.id},
        include={"order_products": True},
    )
    return {"status": status.HTTP_200_OK}


@router.patch(
    "/status",
    response_model=OrderWithoutRelations,
    dependencies=[Depends(RoleChecker(["admin"]))],
)
async def update_order_status(
    id: str, order_status_in: OrderStatus
) -> Optional[Order]:
    order = await Order.prisma().update(
        where={
            "id": id,
        },
        data={"status": order_status_in},
    )
    return order
