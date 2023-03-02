from datetime import datetime

from beanie import Document, Indexed
from pydantic import BaseModel, Field

from product_service.models.enums import OrderStatus


class OrderOptional(BaseModel):
    status: OrderStatus = OrderStatus.pending
    cost: float | None
    tax: float | None
    total: float | None
    currency: str | None


class OrderBase(OrderOptional):
    cart_id: Indexed(str, unique=False)


class OrderCreate(OrderBase):
    pass


class OrderUpdate(OrderOptional):
    pass


class OrderInDBBase(OrderBase):
    created_at: datetime | None = Field(default_factory=datetime.now)
    updated_at: datetime | None = Field(default_factory=datetime.now)


class Order(OrderInDBBase, Document):

    class Config:
        orm_mode = True


class OrderInDB(OrderInDBBase):
    pass
