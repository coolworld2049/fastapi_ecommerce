from product_service.crud.base import CRUDBase
from product_service.models.order import Order, OrderCreate, OrderUpdate


class CRUDOrder(CRUDBase[Order, OrderCreate, OrderUpdate]):
    pass


order = CRUDOrder(Order)
