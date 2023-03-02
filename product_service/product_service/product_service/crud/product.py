from product_service.crud.base import CRUDBase
from product_service.models.product import Product, ProductCreate, ProductUpdate


class CRUDProduct(CRUDBase[Product, ProductCreate, ProductUpdate]):
    pass


product = CRUDProduct(Product)
