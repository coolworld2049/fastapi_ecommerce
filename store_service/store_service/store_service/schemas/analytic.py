from pydantic import BaseModel

from store_service.schemas.request_params import RequestParams


class AnalyticResponse(BaseModel):
    request_params: RequestParams
    report: dict | None
    elapsed_time_sec: float | int | None
    details: dict | None


class SalesRevenue(BaseModel):
    analytic_response: dict | AnalyticResponse
    order_count: int | None
    revenue: float | None
    products: list[dict] | None


class QuantitySoldCategory(BaseModel):
    category_id: str | None
    category: dict | None
    quantity_sold_products_by_status: int | None
