from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi.params import Param
from prisma.enums import OrderStatus
from prisma.models import Category, Product, Order, OrderProduct
from prisma.partials import ProductWithoutRelations
from pydantic import BaseModel

from store_service.api.api_v1.deps import params
from store_service.api.api_v1.deps.base import RoleChecker
from store_service.api.api_v1.deps.params import RequestParams

router = APIRouter()


class SalesRevenue(BaseModel):
    request_params: RequestParams
    start_datetime: datetime
    end_datetime: datetime
    report_created_at: datetime = datetime.now()
    order_count: int
    revenue: float
    products: list[dict] | None


@router.get(
    "/sales/revenue",
    response_model=SalesRevenue,
    dependencies=[Depends(RoleChecker(Category, ["admin"]))],
)
async def sales_revenue(
        _start_datetime: datetime = Param(
            datetime.now().replace(month=datetime.now().month - 1),
            description="ISO 8601 format",
        ),
        _end_datetime: datetime = Param(datetime.now(), description="ISO 8601 format"),
        products: bool = True,
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
    cost = {"cost": True}
    orders_for_period = await Order.prisma().group_by(
        ["id", "user_id"],
        sum=cost,
        having={
            "updated_at": {
                "_min": {"gt": _start_datetime},
                "_max": {"lt": _end_datetime},
            }
        },
        order={"user_id": "asc"},
        **request_params.dict(exclude_none=True),
    )
    order_ids = list(map(lambda x: x.get("id"), orders_for_period))
    orders_products = await OrderProduct.prisma().find_many(
        where={"order_id": {"in": order_ids}}, include={"order": True, "product": True}
    )
    revenue = sum([x.product.price for x in orders_products])
    products_in_order_products = [
        {
            "product": {**x.product.dict(exclude_none=True)},
            "in_orders": [
                x.order_id for y in orders_products if x.order_id == y.order_id
            ],
        }
        for x in orders_products
    ] if products else None
    _sales_revenue = SalesRevenue(
        start_datetime=_start_datetime,
        end_datetime=_end_datetime,
        request_params=request_params,
        products=products_in_order_products,
        order_count=len(order_ids),
        revenue=revenue,
    )
    return _sales_revenue


'''
Получение списка клиентов, которые сделали более чем N покупок в последнее время.
'''


@router.get(
    "/customer/purchases",
    response_model=list[dict],
    dependencies=[Depends(RoleChecker(Category, ["admin"]))],
)
async def customer_purchases(
        _start_datetime: datetime = Param(
            datetime.now().replace(month=datetime.now().month - 1),
            description="ISO 8601 format",
        ),
        _end_datetime: datetime = Param(datetime.now(), description="ISO 8601 format"),
        request_params: RequestParams = Depends(
            params.parse_query_params(
                range_example="[0,100]",
                order_example='{"user_id": "asc"}',
                where_example='{"status": "completed"}',
                where_add_description=f"""`status`=`{[x.name for x in OrderStatus]}`""",
            )
        ),
) -> list[dict]:
    products = await Product.prisma().find_many(
        include={"order_products": True},
        take=request_params.take,
        skip=request_params.skip,
    )

    class SalesAnalysis(BaseModel):
        start_datetime: datetime = _start_datetime
        end_datetime: datetime = _end_datetime
        report_created_at: datetime = datetime.now()
        product: ProductWithoutRelations
        order_status: OrderStatus
        count: int
        avg_cost: float

    cost = {"cost": True}
    group_by = await Order.prisma().group_by(
        ["user_id"],
        min=cost,
        max=cost,
        sum=cost,
        avg=cost,
        having={
            "updated_at": {
                "_min": {"gt": _start_datetime},
                "_max": {"lt": _end_datetime},
            }
        },
        **request_params.dict(exclude_none=True),
    )
    return group_by
