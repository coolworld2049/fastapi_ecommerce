from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi.params import Param
from prisma.enums import OrderStatus
from prisma.models import Category, Product, Order

from store_service.api.api_v1.deps import params
from store_service.api.api_v1.deps.base import RoleChecker
from store_service.api.api_v1.deps.params import RequestParams

router = APIRouter()


@router.get(
    "/orders",
    response_model=list[dict],
    dependencies=[Depends(RoleChecker(Category, ["admin"]))],
)
async def orders(
    start_date: datetime = Param(
        datetime.now().replace(year=datetime.now().year - 1),
        description="ISO 8601 format",
    ),
    end_date: datetime = Param(datetime.now(), description="ISO 8601 format"),
    request_params: RequestParams = Depends(
        params.parse_query_params(
            range_example="[0,100]",
            order_example='{"user_id": "asc"}',
            where_example='{"status": "completed"}',
            where_add_description=f"""`status`=`{[x.name for x in OrderStatus]}`""",
        )
    ),
) -> list[dict]:
    products = await Product.prisma().find_many()
    cost = {"cost": True}
    group_by = await Order.prisma().group_by(
        ["user_id"],
        min=cost,
        max=cost,
        sum=cost,
        avg=cost,
        having={"updated_at": {"_min": {"gt": start_date}, "_max": {"lt": end_date}}},
        count={"product_ids": True},
        **request_params.dict(exclude_none=True),
    )
    return group_by
