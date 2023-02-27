from datetime import datetime
from datetime import timedelta

from jose import jwt

from order_service import schemas
from order_service.core.config import get_app_settings
from order_service.models import UserRole


def create_access_token(
    sub: str,
    role: UserRole,
    expires_delta: timedelta = None,
) -> schemas.Token:
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(
            minutes=get_app_settings().ACCESS_TOKEN_EXPIRE_MINUTES,
        )
    to_encode = {
        "expires_delta": str(expire),
        "sub": str(sub),
        "role": role.name,
    }
    encoded_jwt = jwt.encode(
        to_encode,
        get_app_settings().JWT_SECRET_KEY,
        algorithm=get_app_settings().JWT_ALGORITHM,
    )

    token = schemas.Token(
        access_token=encoded_jwt, token_type="bearer", **to_encode
    )
    return token
