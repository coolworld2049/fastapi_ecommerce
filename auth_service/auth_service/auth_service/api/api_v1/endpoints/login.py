from typing import Any

from fastapi import APIRouter
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service import crud, schemas
from auth_service.api.deps import database
from auth_service.api.errors.custom_exception import (
    BadCredentialsException,
    InactiveUserException,
)
from auth_service.services import jwt

router = APIRouter()


@router.post("/login/access-token", response_model=schemas.Token)
async def login_access_token(
    db: AsyncSession = Depends(database.get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = await crud.user.authenticate(
        email=form_data.username,
        password=form_data.password,
        db=db,
    )
    if not user:
        raise BadCredentialsException
    elif not user.is_active:
        raise InactiveUserException
    token = jwt.encode_access_token(sub=user.id, user=user)
    return token.dict()
