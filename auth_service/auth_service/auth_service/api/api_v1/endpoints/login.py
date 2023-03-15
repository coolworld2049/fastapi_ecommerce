from typing import Any

from fastapi import APIRouter
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import Response

from auth_service import crud, schemas, models
from auth_service.api.deps import database
from auth_service.api.errors.custom_exception import (
    BadCredentialsException,
    InactiveUserException,
    InvalidVerificationCodeException,
)
from auth_service.services import jwt

router = APIRouter()


@router.post("/login/access-token", response_model=schemas.Token)
async def login_access_token(
    db: AsyncSession = Depends(database.get_db),
    form_data: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm),
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


@router.get("/verify_email/{token}")
async def verify_me(token: str, db: AsyncSession = Depends(database.get_db)):
    user = await crud.user.get_by_col(
        db, col=models.User.verification_code, val=token
    )
    user = await crud.user.verify_token(db, db_obj=user, token=token)
    if not user:
        raise InvalidVerificationCodeException
    return Response(
        status_code=status.HTTP_200_OK, content="Account verified successfully"
    )
