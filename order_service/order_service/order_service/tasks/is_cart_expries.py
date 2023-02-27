from datetime import datetime

from sqlalchemy import Select, select, Result
from sqlalchemy.ext.asyncio import AsyncSession

from order_service import models, schemas
from order_service.core.celery_app import celery_app


@celery_app.task(acks_late=True)
async def is_cart_expries(db: AsyncSession, cart_id: int):
    q: Select = select(models.Cart).where(models.Cart.id == cart_id)
    result: Result = await db.execute(q)
    cart: models.Cart = result.scalar()
    msg = f"Cart deleted due to expired in {cart.expires_at}"
    if cart.expires_at >= datetime.now():
        await db.delete(cart)
        return schemas.Msg(msg=msg)
