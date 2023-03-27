from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service import crud, models
from auth_service.api.exceptions import (
    PermissionDeniedException,
    CouldNotValidateCredentialsException,
    AccountNotVerifiedException,
)
from auth_service.core.config import get_app_settings
from auth_service.db import session
from auth_service.services.jwt import decode_access_token

oauth2Scheme = OAuth2PasswordBearer(
    tokenUrl=f"{get_app_settings().api_prefix}/login/access-token"
)


async def _get_current_user(
    db: AsyncSession = Depends(session.get_db),
    token: str = Depends(oauth2Scheme),
) -> models.User:
    token_data = decode_access_token(token)
    user = await crud.user.get(db=db, id=int(token_data.sub))
    if not user:
        raise CouldNotValidateCredentialsException
    return user


async def get_current_user(
    user: models.User = Depends(_get_current_user),
) -> models.User:
    if get_app_settings().TEST_USE_USER_CHECKS:
        if not user.is_verified:
            raise AccountNotVerifiedException
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
        self, current_user: models.User = Depends(get_current_user)
    ):
        if current_user:
            try:
                current_user.role
            except AttributeError as e:
                logger.error(e)
            if get_app_settings().TEST_USE_RBAC:
                if current_user.role not in self.roles:
                    raise PermissionDeniedException