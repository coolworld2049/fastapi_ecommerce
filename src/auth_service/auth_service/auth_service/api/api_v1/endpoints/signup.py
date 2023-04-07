from fastapi import APIRouter
from fastapi import Depends
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.exceptions import HTTPException

import auth_service.api.deps.db
from auth_service import crud, schemas
from auth_service.api.exceptions import DuplicateUserException
from auth_service.core.config import get_app_settings
from auth_service.models import UserRoleEnum
from auth_service.services.email import Email

router = APIRouter()


@router.post(
    "/client",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
)
async def signup_client(
    user_in: schemas.UserCreateOpen,
    db: AsyncSession = Depends(auth_service.api.deps.db.get_db),
):
    user = await crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise DuplicateUserException
    obj_in = schemas.UserCreate(
        role=UserRoleEnum.client, **user_in.dict(exclude_unset=True)
    )
    user = await crud.user.create(db, obj_in=obj_in)
    if get_app_settings().USE_EMAILS:
        email = Email(EmailStr(get_app_settings().SMTP_FROM))
        res = await crud.user.send_email_for_verif(
            db,
            db_obj=user,
            email=email,
        )
        if not res:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="There was an error sending email",
            )
    return {"detail": "The confirmation code has been sent to your email"}
