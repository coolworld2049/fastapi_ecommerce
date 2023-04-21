from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.api.deps.db import get_db
from auth_service import crud, models
from auth_service.api.exceptions import (
    PermissionDeniedException,
    CouldNotValidateCredentialsException,
    AccountNotVerifiedException, )
from auth_service.core.config import get_app_settings
from auth_service.services.jwt import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{get_app_settings().api_prefix}/login/access-token"
)


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> models.User:
    token_data = decode_access_token(token)
    user = await crud.user.get(db=db, id=int(token_data.sub))
    if not user:
        raise CouldNotValidateCredentialsException
    return user


async def get_verified_current_user(
    user=Depends(get_current_user),
):
    if get_app_settings().USE_EMAILS:
        if not user.is_verified:
            raise AccountNotVerifiedException
    return user


async def get_active_current_user(
    user=Depends(get_verified_current_user),
):
    if not user.is_active:
        raise AccountNotVerifiedException
    return user


class RoleChecker:
    def __init__(
        self,
        roles: list,
    ):
        self.roles = roles

    async def __call__(
        self, current_user: models.User = Depends(get_active_current_user)
    ):
        if current_user:
            try:
                current_user.role
            except AttributeError as e:
                logger.error(e)
            if get_app_settings().USE_RBAC:
                if current_user.role not in self.roles:
                    raise PermissionDeniedException
