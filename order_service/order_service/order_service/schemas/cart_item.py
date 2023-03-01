from pydantic import BaseModel


class CartItemBase(BaseModel):
    cart_id: int | None
    product_id: int | None


class CartItemCreate(CartItemBase):
    pass


class CartItemUpdate(CartItemBase):
    pass


class CartItemInDBBase(CartItemBase):
    id: int | None = None

    class Config:
        orm_mode = True


class CartItem(CartItemInDBBase):
    pass


class CartItemInDB(CartItemInDBBase):
    pass
