from datetime import datetime

from beanie import Document, Indexed
from pydantic import BaseModel, Field

from product_service.models.enums import CartStatus


class CartBase(BaseModel):
    user_id: Indexed(str, unique=False)
    status: CartStatus = CartStatus.active
    expires_at: datetime | None = None


class CartCreate(CartBase):
    pass


class CartUpdate(CartBase):
    pass


class CartInDBBase(CartBase):
    created_at: datetime | None = Field(default_factory=datetime.now)
    updated_at: datetime | None = Field(default_factory=datetime.now)


class Cart(CartInDBBase, Document):

    class Config:
        orm_mode = True


class CartInDB(CartInDBBase):
    pass
