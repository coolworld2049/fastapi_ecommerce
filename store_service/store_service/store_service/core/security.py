from datetime import timedelta, datetime

from jose import jwt

from store_service.core.config import settings


def create_access_token(
    sub: str,
    expires_delta: timedelta = None,
) -> dict[str, str]:
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        )
    to_encode = {
        "expires_delta": str(expire),
        "sub": sub,
    }
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return {"access_token": encoded_jwt}
