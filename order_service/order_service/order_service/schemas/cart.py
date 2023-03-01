from datetime import datetime

from pydantic import BaseModel


class CartBase(BaseModel):
    expires_at: datetime | None


class CartCreate(CartBase):
    pass


class CartUpdate(CartBase):
    pass


class CartInDBBase(CartBase):
    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        orm_mode = True


class Cart(CartInDBBase):
    pass


class CartInDB(CartInDBBase):
    pass
