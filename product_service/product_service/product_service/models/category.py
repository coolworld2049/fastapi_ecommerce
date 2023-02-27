from beanie import Document, Indexed
from pydantic import BaseModel


class CategoryBase(BaseModel):
    name: Indexed(str, unique=True)
    description: str


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    description: str


class CategoryInDBBase(CategoryBase):
    pass


class Category(CategoryInDBBase, Document):
    class Config:
        orm_mode = True


class CategoryInDB(CategoryInDBBase):
    pass
