from fastapi import APIRouter
from fastapi import Depends
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from auth_service import crud, schemas
from auth_service.api.deps import database
from auth_service.api.errors.custom_exception import DuplicateUserException
from auth_service.core.config import get_app_settings
from auth_service.models import UserRole
from auth_service.services.email import Email

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
    user_in_: dict = user_in.dict()
    user_in_.update({"role": UserRole.customer})
    user_in = schemas.UserCreate(**user_in_)
    user = await crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise DuplicateUserException
    user = await crud.user.create(db, obj_in=user_in)
    email = Email(EmailStr(get_app_settings().EMAIL_FROM))
    await crud.user.send_verif_email(
        db,
        db_obj=user,
        email=email,
        verify_token_url=get_app_settings().origin_url + "/verify/email",
    )
    return user
