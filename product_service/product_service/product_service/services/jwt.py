from datetime import datetime
from datetime import timedelta

from jose import jwt

from product_service.core.config import settings
from product_service.models.enums import UserRole
from product_service.models.token import Token


def create_access_token(
    sub: str,
    role: UserRole,
    expires_delta: timedelta = None,
) -> Token:
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        )
    to_encode = {
        "expires_delta": str(expire),
        "sub": sub,
        "role": role.name,
    }
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    token = Token(
        access_token=encoded_jwt, token_type="bearer", **to_encode
    )
    return token
