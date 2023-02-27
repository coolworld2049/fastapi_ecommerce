from loguru import logger
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from order_service.crud.base import CRUDBase
from order_service.models import Cart
from order_service.schemas import CartCreate
from order_service.schemas import CartUpdate


class CRUDCart(CRUDBase[Cart, CartCreate, CartUpdate]):
    async def add_to_cart(
        self, db: AsyncSession, *, obj_in: CartCreate
    ) -> Cart:
        db_obj = self.model(**obj_in.dict(exclude_none=True))
        try:
            db.add(db_obj)
            await db.commit()
            await db.refresh(db_obj)
        except IntegrityError as e:
            logger.error(e.args)
        return db_obj


cart = CRUDCart(Cart)
