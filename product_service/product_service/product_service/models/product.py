from beanie import Document, Indexed
from pydantic import BaseModel


class ProductBase(BaseModel):
    title: Indexed(str, unique=True)
    category_name: str
    stock: int
    price: float
    description: str


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    pass


class ProductInDBBase(ProductBase):
    pass


class Product(ProductInDBBase, Document):
    class Config:
        orm_mode = True


class ProductInDB(ProductInDBBase):
    pass
