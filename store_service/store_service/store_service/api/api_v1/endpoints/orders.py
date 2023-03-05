from typing import Optional, Any

from fastapi import APIRouter, Depends
from prisma.enums import OrderStatus
from prisma.models import Order, User, Product
from prisma.partials import OrderWithoutRelations
from starlette import status
from starlette.exceptions import HTTPException

from store_service.api.api_v1.deps import params
from store_service.api.api_v1.deps.base import RoleChecker, get_current_active_user
from store_service.api.api_v1.deps.params import RequestParams

router = APIRouter()


@router.get(
    "/all",
    response_model=list[OrderWithoutRelations],
    dependencies=[Depends(RoleChecker(Order, ["admin", "manager", "customer"]))],
)
async def read_orders(
    request_params: RequestParams = Depends(params.parse_query_params()),
) -> list[Order]:
    order = await Order.prisma().find_many(**request_params.dict(exclude_none=True))
    return order


@router.get(
    "/",
    response_model=Order,
    dependencies=[Depends(RoleChecker(Order, ["admin", "customer"]))],
)
async def read_current_order(
    current_user: User = Depends(get_current_active_user),
) -> Optional[Order]:
    user = await User.prisma().find_unique(
        where={"id": current_user.id},
        include={"orders": True},
    )
    order = [x.id for x in user.orders if x.status == OrderStatus.pending]
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return await Order.prisma().find_unique(where={"id": str(*order)})


@router.get(
    "/cost",
    response_model=dict,
    dependencies=[Depends(RoleChecker(Order, ["admin", "customer"]))],
)
async def my_order_cost(
    current_user: User = Depends(get_current_active_user),
) -> dict:
    user = await User.prisma().find_unique(
        where={"id": current_user.id},
        include={"orders": True},
    )
    _order = [x.id for x in user.orders if x.status == OrderStatus.pending]
    if not _order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    order = await Order.prisma().find_unique(
        where={"id": str(*_order)}, include={"products": True}
    )

    cost = float(sum([x.price for x in order.products]))
    order = await Order.prisma().update(
        data={"cost": {"set": cost}},
        where={"id": str(*_order)},
        include={"products": True},
    )
    if cost == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="There are no products in the order",
        )
    return {"cost": cost}


@router.post(
    "/",
    response_model=OrderWithoutRelations,
    dependencies=[Depends(RoleChecker(Order, ["admin", "customer"]))],
)
async def create_order(
    current_user: User = Depends(get_current_active_user),
) -> Optional[Order]:
    order = await Order.prisma().find_many(
        where={"user_id": current_user.id, "status": OrderStatus.pending}
    )
    if order:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Order with pending status already exists",
        )

    order = await Order.prisma().create(
        data={
            "status": OrderStatus.pending,
            "user": {"connect": {"id": current_user.id}},
        }
    )
    return order


@router.patch(
    "/status",
    response_model=OrderWithoutRelations,
    dependencies=[Depends(RoleChecker(Order, ["admin"]))],
)
async def update_order_status(id: str, order_status_in: OrderStatus) -> Optional[Order]:
    return await Order.prisma().update(
        where={
            "id": id,
        },
        data={"status": order_status_in},
    )


@router.patch(
    "/product/add",
    response_model=OrderWithoutRelations,
    dependencies=[Depends(RoleChecker(Order, ["admin", "customer"]))],
)
async def add_products_to_order(
    product_id: str,
    current_user: User = Depends(get_current_active_user),
) -> Optional[Order]:
    user = await User.prisma().find_unique(
        where={"id": current_user.id},
        include={"orders": True},
    )
    product = await Product.prisma().find_unique(where={"id": product_id})
    order_id = str(*[x.id for x in user.orders if x.status == OrderStatus.pending])
    if not order_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This product can`t be added to the order",
        )
    order = await Order.prisma().update(
        data={
            "cost": {"increment": float(product.price)},
            "products": {"connect": [{"id": product_id}]},
        },
        where={"id": order_id},
        include={"products": True},
    )
    if product_id in order.product_ids:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This product is already on order.",
        )
    product = await Product.prisma().update(
        data={"stock": {"decrement": 1}},
        where={"id": product_id},
        include={"orders": True},
    )
    return order


@router.patch(
    "/product/delete",
    response_model=OrderWithoutRelations,
    dependencies=[Depends(RoleChecker(Order, ["admin", "customer"]))],
)
async def delete_product_from_order(
    product_id: str,
    current_user: User = Depends(get_current_active_user),
) -> Optional[Order]:
    user = await User.prisma().find_unique(
        where={"id": current_user.id},
        include={"orders": True},
    )
    product = await Product.prisma().find_unique(where={"id": product_id})
    order_id = str(*[x.id for x in user.orders if x.status == OrderStatus.pending])
    if not order_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
        )
    order = await Order.prisma().update(
        data={
            "cost": {"decrement": float(product.price)},
            "products": {"disconnect": [{"id": product_id}]},
        },
        where={"id": order_id},
        include={"products": True},
    )
    if product_id not in order.product_ids:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This product is already deleted from the order",
        )
    product = await Product.prisma().update(
        data={"stock": {"increment": 1}},
        where={"id": product_id},
        include={"orders": True},
    )
    return order


@router.delete(
    "/",
    dependencies=[Depends(RoleChecker(Order, ["admin", "customer"]))],
)
async def delete_order(
    current_user: User = Depends(get_current_active_user),
) -> dict[str, Any]:
    user = await User.prisma().find_unique(
        where={"id": current_user.id},
        include={"orders": True},
    )
    order = [x.id for x in user.orders if x.status == OrderStatus.pending]
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    await Order.prisma().delete(where={"id": str(*order)}, include={"products": True})
    return {"status": status.HTTP_200_OK}
