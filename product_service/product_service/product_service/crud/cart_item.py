from product_service.crud.base import CRUDBase
from product_service.models.cart_item import CartItem, CartItemCreate, CartItemUpdate


class CRUDCartItem(CRUDBase[CartItem, CartItemCreate, CartItemUpdate]):
    pass


cart_item = CRUDCartItem(CartItem)
