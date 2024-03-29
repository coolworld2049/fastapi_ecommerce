import json

from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from jose import jwt

from store_service.api.api_v1.deps.custom_exception import (
    BadCredentialsException,
    PermissionDeniedException,
)
from store_service.core.config import get_app_settings
from store_service.schemas.user import User

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=get_app_settings().api_prefix + "/store_service/login"
)


def jwt_decode(token: str):
    payload = jwt.decode(
        token=token,
        key=get_app_settings().JWT_SECRET_KEY,
        algorithms=get_app_settings().JWT_ALGORITHM,
        options={"verify_aud": False},
    )
    sub = payload.get("sub")
    if not sub:
        raise BadCredentialsException
    return payload


async def get_current_user(
    token: str = Depends(oauth2_scheme),
) -> User:
    try:
        payload = jwt_decode(token)
    except JWTError:
        raise BadCredentialsException

    user = User(**json.loads(payload.get("user")))
    if user is None:
        raise BadCredentialsException
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_active_superuser(
    current_user: User = Depends(get_current_active_user),
) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=400,
            detail="This user doesn't have enough privileges",
        )
    return current_user


class RoleChecker:
    def __init__(
        self,
        roles: list = None,
    ):
        self.roles = roles

    async def __call__(
        self, current_user: User = Depends(get_current_active_user)
    ):
        if current_user.role not in self.roles:
            raise PermissionDeniedException
