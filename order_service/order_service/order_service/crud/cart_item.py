from order_service.crud.base import CRUDBase
from order_service.models import CartItem
from order_service.schemas import CartItemCreate
from order_service.schemas import CartItemUpdate


class CRUDCartItem(CRUDBase[CartItem, CartItemCreate, CartItemUpdate]):
    pass


cart_item = CRUDCartItem(CartItem)
