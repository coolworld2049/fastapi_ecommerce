from typing import Any

from loguru import logger
from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from order_service import crud, models, schemas
from order_service.core.config import get_app_settings
from order_service.crud.base import CRUDBase
from order_service.models import Order
from order_service.schemas import OrderCreate
from order_service.schemas import OrderUpdate


class CRUDOrder(CRUDBase[Order, OrderCreate, OrderUpdate]):
    async def get_by_user_id(self, db: AsyncSession, *, id: Any) -> Order:
        q: Select = select(self.model).where(self.model.user_id == id)
        result: Result = await db.execute(q)
        return result.scalar()

    async def create(self, db: AsyncSession, *, obj_in: OrderCreate) -> Order:
        cart_in = schemas.Cart(
            expires_at=get_app_settings().cart_expires_timestamp,
        )
        cart_db_obj: models.Cart = await crud.cart.create(db, obj_in=cart_in)

        db_obj = self.model(**obj_in.dict(exclude_none=True))
        db_obj.cart_id = cart_db_obj.id

        try:
            db.add(db_obj)
            await db.commit()
            await db.refresh(db_obj)
            return db_obj
        except IntegrityError as e:
            logger.error(e.args)
            raise


order = CRUDOrder(Order)
