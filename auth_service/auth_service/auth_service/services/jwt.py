import json
from datetime import datetime
from datetime import timedelta

from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service import schemas, models
from auth_service.api.errors.custom_exception import BadCredentialsException
from auth_service.core.config import get_app_settings


def encode_access_token(
    sub: str,
    user: models.User,
) -> schemas.Token:
    expires_delta = datetime.now() + timedelta(
        minutes=get_app_settings().ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    token_payload = schemas.TokenPayload(
        sub=sub,
        user=json.dumps(schemas.User(**user.__dict__).dict(), default=str),
        expires_delta=str(expires_delta),
    )
    access_token = jwt.encode(
        claims=token_payload.dict(exclude_none=True),
        key=get_app_settings().JWT_SECRET_KEY,
        algorithm=get_app_settings().JWT_ALGORITHM,
    )
    token = schemas.Token(access_token=access_token)
    return token


def decode_access_token(db: AsyncSession, token: str) -> schemas.TokenPayload:
    try:
        payload = jwt.decode(
            token=token,
            key=get_app_settings().JWT_SECRET_KEY,
            algorithms=get_app_settings().JWT_ALGORITHM,
            options={"verify_aud": False},
        )
        return schemas.TokenPayload(**payload)
    except JWTError:
        raise BadCredentialsException
