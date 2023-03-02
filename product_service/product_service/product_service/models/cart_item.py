from beanie import Document, Indexed
from pydantic import BaseModel


class CartItemBase(BaseModel):
    cart_id: Indexed(str, unique=False)
    product_id: str


class CartItemCreate(CartItemBase):
    pass


class CartItemUpdate(CartItemBase):
    pass


class CartItemInDBBase(CartItemBase):
    pass


class CartItem(CartItemInDBBase, Document):

    class Config:
        orm_mode = True


class CartItemInDB(CartItemInDBBase):
    pass
