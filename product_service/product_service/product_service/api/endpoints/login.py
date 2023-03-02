from datetime import timedelta
from typing import Any

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

from product_service import crud
from product_service.api.dependencies import auth
from product_service.api.dependencies.auth import oauth2Scheme
from product_service.core.config import settings
from product_service.models.token import Token
from product_service.models.user import UserRole, User
from product_service.services import jwt

router = APIRouter()


@router.post("/login/access-token", response_model=Token)
async def login_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    try:
        user = await crud.user.authenticate(
            email=form_data.username,
            password=form_data.password,
        )
    except HTTPException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=e.detail
        )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Incorrect email or password",
        )
    elif not crud.user.is_active(user):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
        )
    exp = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = jwt.create_access_token(
        sub=user.id.__str__(),
        role=UserRole(user.role),
        expires_delta=exp,
    )
    return token


@router.post("/login/test-token", response_model=User)
def test_token(
    current_user: User = Depends(auth.get_current_user),
) -> Any:
    """
    Test access token
    """
    return current_user


@router.get("/logout")
def logout(
    request: Request,
    current_user: User = Depends(auth.get_current_user),  # noqa
) -> Any:
    """
    Logout
    """
    response = JSONResponse({"status": "stub"})
    response.delete_cookie(key=oauth2Scheme.token_name)
    return response
