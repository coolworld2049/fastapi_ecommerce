from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from jose import jwt
from starlette import status

from product_service import crud
from product_service.core.config import settings
from product_service.models.token import TokenPayload
from product_service.models.user import User

oauth2Scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.api_prefix}/login/access-token"
)


async def get_current_user(
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
            key=settings.JWT_SECRET_KEY,
            algorithms=settings.JWT_ALGORITHM,
            options={"verify_aud": False},
        )
        subject: str = payload.get("sub")
        if not subject:
            raise credentials_exception
        token_data = TokenPayload(sub=subject)
    except JWTError:
        raise credentials_exception

    user = await crud.user.get(id=token_data.sub)
    if user is None:
        raise credentials_exception
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
