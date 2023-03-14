from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service import crud, models
from auth_service.api.deps import database
from auth_service.api.errors.custom_exception import (
    PermissionDeniedException,
    BadCredentialsException,
)
from auth_service.core.config import get_app_settings
from auth_service.services.jwt import decode_access_token

oauth2Scheme = OAuth2PasswordBearer(
    tokenUrl=f"{get_app_settings().api_prefix}/login/access-token"
)


async def get_current_user(
    db: AsyncSession = Depends(database.get_db),
    token: str = Depends(oauth2Scheme),
) -> models.User:
    token_data = decode_access_token(db, token)
    user = await crud.user.get_by_id(db=db, id=token_data.sub)
    if user is None:
        raise BadCredentialsException
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
        try:
            current_user.role
        except AttributeError:
            logger.error("'User' object has no attribute 'role'")
        if current_user.role not in self.roles:
            if get_app_settings().DEBUG:
                logger.warning(
                    f"Details: current_user role is '{current_user.role}', required roles: {self.roles}"
                )
            raise PermissionDeniedException
