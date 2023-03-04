from typing import Any

from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from employee_service import schemas
from employee_service import models
from employee_service.api.dependencies import auth, database
from employee_service.core.celery_app import celery_app

router = APIRouter()


# noinspection PyUnusedLocal
@router.post("/test-celery/", response_model=schemas.Msg, status_code=201)
async def test_celery(
    msg: schemas.Msg,
    current_user: models.User = Depends(auth.get_current_active_superuser),
) -> Any:
    """
    Test Celery worker.
    """
    celery_app.send_task("employee_service.worker.test_celery", args=[msg.msg])
    return {"msg": "Word received"}


# noinspection PyUnusedLocal
@router.post(
    "/test-celery/is_cart_expries", response_model=schemas.Msg, status_code=201
)
async def test_celery_is_cart_expries(
    cart_id: int,
    db: AsyncSession = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_active_superuser),
) -> Any:
    """
    Test Celery task is_cart_expries.
    """
    celery_app.send_task("employee_service.tasks.is_cart_expries", args=(db, cart_id))
    return {"msg": "Word received"}
