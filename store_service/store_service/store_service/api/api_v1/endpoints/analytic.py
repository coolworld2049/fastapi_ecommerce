import time
from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi.params import Param
from prisma.enums import OrderStatus
from prisma.models import Order, OrderProduct
from pydantic import BaseModel

from store_service.api.api_v1.deps import params
from store_service.api.api_v1.deps.base import RoleChecker
from store_service.api.api_v1.deps.params import RequestParams

router = APIRouter()


class AnalyticResponse(BaseModel):
    request_params: RequestParams
    report: dict | None
    elapsed_time_sec: float | None
    details: dict | None


class SalesRevenue(BaseModel):
    analytic_response: dict | AnalyticResponse
    order_count: int | None
    revenue: float | None
    products: list[dict] | None


async def get_orders_for_period(
    start_datetime: datetime, end_datetime: datetime, request_params: RequestParams
):
    cost = {"cost": True}
    orders_for_period = await Order.prisma().group_by(
        ["id"],
        sum=cost,
        having={
            "updated_at": {
                "_min": {"gt": start_datetime},
                "_max": {"lt": end_datetime},
            }
        },
        order={"id": "asc"},
        **request_params.dict(exclude_none=True),
    )
    order_ids = list(map(lambda x: x.get("id"), orders_for_period))
    orders_products = await OrderProduct.prisma().find_many(
        where={"order_id": {"in": order_ids}}, include={"order": True, "product": True}
    )
    return orders_products


@router.get(
    "/sales",
    response_model=SalesRevenue,
    dependencies=[Depends(RoleChecker(roles=["admin"]))],
)
async def sales_analytics(
    start_datetime: datetime = Param(
        datetime.now().replace(year=datetime.now().year - 1),
        description="ISO 8601 format",
    ),
    end_datetime: datetime = Param(datetime.now(), description="ISO 8601 format"),
    products: bool = True,
    in_orders: bool = False,
    buyers: bool = False,
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
    orders_products = await get_orders_for_period(
        start_datetime, end_datetime, request_params
    )
    orders_product_users = [x.order.user_id for x in orders_products]
    revenue = sum([x.product.price for x in orders_products])
    products_in_order_products = (
        [
            {
                "product": x.product.id,
                "in_orders": {y.order_id for y in orders_products}
                if in_orders
                else None,
                "buyers": {
                    "customers": {
                        "ids": {
                            y.order.user_id
                            for y in orders_products
                            if y.product_id == x.product_id
                        }
                    }
                }
                if buyers
                else None,
            }
            for x in orders_products
        ]
        if products
        else None
    )
    end = time.time()
    analytic_response = AnalyticResponse(
        request_params=request_params,
        report={
            "start_datetime": start_datetime,
            "end_datetime": end_datetime,
            "created_at": datetime.now(),
        },
        elapsed_time_sec=f"{end - start}",
        details={"product_count": len(products_in_order_products)},
    )
    _sales_revenue = SalesRevenue(
        analytic_response=analytic_response,
        products=products_in_order_products,
        order_count=len({x.order_id for x in orders_products}),
        revenue=revenue,
    )
    return _sales_revenue


class QuantitySoldCategory(BaseModel):
    category_id: str | None
    quantity_sold_products_by_status: int | None


@router.get(
    "/sales/category",
    response_model=dict[str, AnalyticResponse | list[QuantitySoldCategory]],
    dependencies=[Depends(RoleChecker(roles=["admin"]))],
)
async def categories_sales_analytic(
    start_datetime: datetime = Param(
        datetime.now().replace(year=datetime.now().year - 1),
        description="ISO 8601 format",
    ),
    end_datetime: datetime = Param(datetime.now(), description="ISO 8601 format"),
    request_params: RequestParams = Depends(
        params.parse_query_params(
            use_order=False,
            order_example=None,
            range_description="Explanation: The range applicable for the 'Order' collection.",
            where_example='{"status": "completed"}',
            where_add_description=f"""`status`=`{[x.name for x in OrderStatus]}`""",
        )
    ),
) -> dict[str, AnalyticResponse | list[QuantitySoldCategory]]:
    start = time.time()
    orders_products = await get_orders_for_period(
        start_datetime, end_datetime, request_params
    )
    sold_product_category_ids = {x.product.category_id for x in orders_products}

    end = time.time()
    analytic_response = AnalyticResponse(
        request_params=request_params,
        report={
            "start_datetime": start_datetime,
            "end_datetime": end_datetime,
            "created_at": datetime.now(),
        },
        elapsed_time_sec=f"{end - start}",
        details={"category_count": len(sold_product_category_ids)},
    )
    quantity_sold_category = {
        "analytic_response": analytic_response,
        "categories": [
            QuantitySoldCategory(
                category_id=x,
                quantity_sold_products_by_status=len(
                    {y.order_id for y in orders_products if y.product.category_id == x}
                ),
            )
            for x in sold_product_category_ids
        ],
    }
    return quantity_sold_category
