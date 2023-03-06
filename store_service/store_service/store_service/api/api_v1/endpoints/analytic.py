import time
from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi.params import Param
from prisma.enums import OrderStatus
from prisma.models import Category, Order, OrderProduct
from pydantic import BaseModel

from store_service.api.api_v1.deps import params
from store_service.api.api_v1.deps.base import RoleChecker
from store_service.api.api_v1.deps.params import RequestParams

router = APIRouter()


class SalesRevenue(BaseModel):
    request_params: RequestParams
    info: dict | None
    order_count: int
    revenue: float
    products: list[dict] | None


@router.get(
    "/sales",
    response_model=SalesRevenue,
    dependencies=[Depends(RoleChecker(Category, ["admin"]))],
)
async def sales_analytics(
        start_datetime: datetime = Param(
            datetime.now().replace(year=datetime.now().year - 1),
            description="ISO 8601 format",
        ),
        end_datetime: datetime = Param(datetime.now(), description="ISO 8601 format"),
        products: bool = True,
        products_in_orders: bool = False,
        customer_purchases: bool = False,
        request_params: RequestParams = Depends(
            params.parse_query_params(
                use_order=False,
                order_example=None,
                range_description="Explanation: The range applicable for the 'Order' collection.",
                where_example='{"status": "completed"}',
                where_add_description=f"""`status`=`{[x.name for x in OrderStatus]}`""",
            )
        ),
) -> SalesRevenue:
    start = time.time()
    cost = {"cost": True}
    orders_for_period = await Order.prisma().group_by(
        ["id", "user_id"],
        sum=cost,
        having={
            "updated_at": {
                "_min": {"gt": start_datetime},
                "_max": {"lt": end_datetime},
            }
        },
        order={"user_id": "asc"},
        **request_params.dict(exclude_none=True),
    )
    order_ids = list(map(lambda x: x.get("id"), orders_for_period))
    orders_products = await OrderProduct.prisma().find_many(
        where={"order_id": {"in": order_ids}}, include={"order": True, "product": True}
    )
    orders_product_users = [x.order.user_id for x in orders_products]
    revenue = sum([x.product.price for x in orders_products])
    products_in_order_products = (
        [
            {
                "product": {**x.product.dict(exclude_none=True)},
                "in_orders": {y.order_id for y in orders_products}
                if products_in_orders
                else None,
                "buyers": {
                    "customers": {"ids": {y.order.user_id for y in orders_products if y.product_id == x.product_id}}
                }
                if customer_purchases
                else None,
            }
            for x in orders_products
        ]
        if products
        else None
    )
    end = time.time()
    info = {
        "report": {
            "start_datetime": start_datetime,
            "end_datetime": end_datetime,
            "created_at": datetime.now()
        },
        "elapsed_time_sec": f"{end - start}",
    }
    _sales_revenue = SalesRevenue(
        request_params=request_params,
        products=products_in_order_products,
        order_count=len(order_ids),
        revenue=revenue,
        info=info
    )
    return _sales_revenue
