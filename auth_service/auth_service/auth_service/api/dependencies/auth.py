from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from jose import jwt
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from auth_service import crud, schemas
from auth_service.api.dependencies import database
from auth_service.api.dependencies.custom_exception import (
    PermissionDeniedException,
)
from auth_service.core.config import get_app_settings
from auth_service.models.user import User

oauth2Scheme = OAuth2PasswordBearer(
    tokenUrl=f"{get_app_settings().api_prefix}/login/access-token"
)


async def get_current_user(
    db: AsyncSession = Depends(database.get_db),
    token: str = Depends(oauth2Scheme),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token=token,
            key=get_app_settings().JWT_SECRET_KEY,
            algorithms=get_app_settings().JWT_ALGORITHM,
            options={"verify_aud": False},
        )
        subject: str = payload.get("sub")
        if not subject:
            raise credentials_exception
        token_data = schemas.TokenPayload(sub=subject)
    except JWTError:
        raise credentials_exception

    user = await crud.user.get_by_id(db=db, id=token_data.sub)
    if user is None:
        raise credentials_exception
    # await authorization_in_db(db, user)
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
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
        roles: list,
    ):
        self.roles = roles

    async def __call__(
        self, current_user: User = Depends(get_current_active_user)
    ):
        if current_user.role not in self.roles:
            if get_app_settings().DEBUG:
                logger.warning(
                    f"Details: current_user role is '{current_user.role}', required roles: {self.roles}"
                )
            raise PermissionDeniedException
