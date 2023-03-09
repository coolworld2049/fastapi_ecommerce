import json
from datetime import datetime
from datetime import timedelta

from jose import jwt

from auth_service import schemas
from auth_service.core.config import get_app_settings
from auth_service.models import User


def create_access_token(
    sub: str,
    user: User,
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
        "user": json.dumps(schemas.User(**user.__dict__).dict(), default=str),
    }
    encoded_jwt = jwt.encode(
        to_encode,
        get_app_settings().JWT_SECRET_KEY,
        algorithm=get_app_settings().JWT_ALGORITHM,
    )

    token = schemas.Token(access_token=encoded_jwt, token_type="bearer", **to_encode)
    return token
