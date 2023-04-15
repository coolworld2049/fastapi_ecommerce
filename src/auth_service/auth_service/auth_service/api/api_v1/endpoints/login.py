from typing import Any

from fastapi import APIRouter
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

import auth_service.api.deps.db
from auth_service import crud, schemas
from auth_service.api.deps.auth import get_active_current_user
from auth_service.api.exceptions import (
    CouldNotValidateCredentialsException,
)
from auth_service.services import jwt

router = APIRouter()


@router.post("/login/access-token", response_model=schemas.Token)
async def login_access_token(
    db: AsyncSession = Depends(auth_service.api.deps.db.get_db),
    form_data: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm),
) -> Any:
    user = await crud.user.authenticate(
        email=form_data.username,
        password=form_data.password,
        db=db,
    )
    if not user or not await get_active_current_user(user):
        raise CouldNotValidateCredentialsException
    token = jwt.encode_access_token(sub=user.id, user=user)
    return token.dict()
