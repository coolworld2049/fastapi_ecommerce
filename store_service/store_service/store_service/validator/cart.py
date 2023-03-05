from datetime import datetime
from typing import Any

from prisma.models import Cart
from prisma.partials import CartCreate
from starlette import status
from starlette.exceptions import HTTPException


class CartValidator:
    def __init__(self, cart: Cart | list[Cart] | Any):
        if isinstance(cart, dict):
            self.cart = CartCreate(**cart)
        else:
            self.cart = cart

    async def is_expire(self):
        async def check(item: Cart | Any):
            if datetime.now() >= item.expires_at.replace(tzinfo=None):
                await item.prisma().update(
                    {"status": CartStatus.inactive}, where={"id": item.id}
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="your cart is expired and inactive",
                )

        if not isinstance(self.cart, list):
            await check(self.cart)
        elif isinstance(self.cart, list):
            for c in self.cart:
                await check(c)
        return self.cart