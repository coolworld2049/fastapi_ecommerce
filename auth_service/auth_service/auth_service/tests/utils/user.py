from typing import Dict

from httpx import AsyncClient
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service import crud, schemas
from auth_service.api.dependencies.auth import oauth2Scheme
from auth_service.core.config import get_app_settings
from auth_service.models.user import User
from auth_service.tests.utils.utils import gen_random_password
from auth_service.tests.utils.utils import random_email


async def user_authentication_headers(
    *,
    client: AsyncClient,
    email: str,
    password: str,
) -> Dict[str, str]:
    data = {"username": email, "password": password}

    r = await client.post(
        f"{get_app_settings().api_v1}/login/access-token", data=data
    )
    token = r.cookies.get(oauth2Scheme.token_name)
    headers = {"Authorization": f"Bearer {token}"}
    return headers


async def create_random_user(db: AsyncSession) -> User:
    email = random_email()
    password = gen_random_password()
    user_in = schemas.UserCreate(
        username=email,
        email=email,
        password=password,
        password_confirm=password,
    )
    user = await crud.user.create(db=db, obj_in=user_in)
    return user


async def authentication_token_from_email(
    *,
    client: AsyncClient,
    email: EmailStr | str,
    db: AsyncSession,
) -> Dict[str, str]:
    """
    Return a valid token for the user with given email.

    If the user doesn't exist it is created first.
    """
    password = gen_random_password()
    user = await crud.user.get_by_email(db, email=email)
    if not user:
        user_in_create = schemas.UserCreate(
            username=email,
            email=email,
            password=password,
            password_confirm=password,
        )
        user = await crud.user.create(db, obj_in=user_in_create)  # noqa
    else:
        user_in_update = schemas.UserUpdate(
            password=password, password_confirm=password
        )
        user = await crud.user.update(
            db, db_obj=user, obj_in=user_in_update
        )  # noqa

    return await user_authentication_headers(
        client=client, email=email, password=password
    )
