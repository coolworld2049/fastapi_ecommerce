from fastapi.security import OAuth2PasswordBearer

from app import crud
from app import schemas
from app.api.dependencies import database
from app.api.dependencies.database import authorization_in_db
from app.core.config import get_app_settings
from app.models.user import User
from fastapi import Depends
from fastapi import HTTPException
from jose import jwt
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

oauth2Scheme = OAuth2PasswordBearer(
    tokenUrl=f"{get_app_settings().api_v1}/login/access-token",
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

    user = await crud.user.get_by_id(db=db, id=int(token_data.sub))
    if user is None:
        raise credentials_exception
    await authorization_in_db(db, user)
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


