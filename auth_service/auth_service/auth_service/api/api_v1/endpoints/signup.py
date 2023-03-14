from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from auth_service import crud, schemas
from auth_service.api.deps import database
from auth_service.api.errors.custom_exception import DuplicateUserException
from auth_service.models import UserRole

router = APIRouter()


@router.post(
    "/customer",
    response_model=schemas.User,
    status_code=status.HTTP_201_CREATED,
)
async def signup_customer(
    user_in: schemas.UserCreateOpen,
    db: AsyncSession = Depends(database.get_db),
):
    user_in.role = UserRole.customer
    user = await crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise DuplicateUserException
    user = await crud.user.create(db, obj_in=user_in)
    return user
