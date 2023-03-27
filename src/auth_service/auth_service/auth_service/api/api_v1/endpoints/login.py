from typing import Any

from fastapi import APIRouter
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service import crud, schemas
from auth_service.core.config import get_app_settings
from auth_service.db import session
from auth_service.api.exceptions import (
    CouldNotValidateCredentialsException,
    InactiveUserException,
    AccountNotVerifiedException,
)
from auth_service.services import jwt

router = APIRouter()


@router.post("/login/access-token", response_model=schemas.Token)
async def login_access_token(
    db: AsyncSession = Depends(session.get_db),
    form_data: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm),
) -> Any:
    user = await crud.user.authenticate(
        email=form_data.username,
        password=form_data.password,
        db=db,
    )
    if not user:
        raise CouldNotValidateCredentialsException
    if get_app_settings().TEST_USE_USER_CHECKS:
        if not user.is_active:
            raise InactiveUserException
        elif not user.is_verified:
            raise AccountNotVerifiedException
    token = jwt.encode_access_token(sub=user.id, user=user)
    return token.dict()
