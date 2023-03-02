from product_service.core.config import settings
from product_service.crud.base import CRUDBase
from product_service.models.cart import Cart
from product_service.models.cart import CartCreate
from product_service.models.cart import CartUpdate
from product_service.models.user import User


class CRUDCart(CRUDBase[Cart, CartCreate, CartUpdate]):

    async def get_active_cart(
        self, user: User
    ) -> int:
        carts = await self.model.find_many({"user_id": user.id}).count()
        return carts

    # noinspection PyShadowingNames
    async def create(
        self, obj_in: CartCreate
    ) -> Cart:
        expires_at = settings.cart_expires_timestamp
        cart_in = obj_in.dict(exclude_none=True)
        cart_in.update({'expires_at': expires_at})
        cart_in = CartCreate(**cart_in)
        cart = await super().create(obj_in=cart_in)
        return cart


cart = CRUDCart(Cart)
