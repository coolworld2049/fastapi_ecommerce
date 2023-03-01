from datetime import datetime

from pydantic import BaseModel

from order_service.models import OrderStatus


class OrderBase(BaseModel):
    user_id: int | None
    status: OrderStatus = OrderStatus.pending
    cost: float | None = None
    tax: float | None = None
    total: float | None = None
    currency: str | None = None


class OrderCreate(OrderBase):
    pass


class OrderUpdate(OrderBase):
    pass


class OrderInDBBase(OrderBase):
    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        orm_mode = True


class Order(OrderInDBBase):
    cart_id: int | None


class OrderInDB(OrderInDBBase):
    pass
