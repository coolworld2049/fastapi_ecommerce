import random
import string
from typing import Dict

import pytest
from faker import Faker
from httpx import AsyncClient

from app import crud, models
from app import schemas
from app.core.config import get_app_settings
from app.models import UserRole
from app.schemas.user import UserCreate
from app.tests.test_data import fake
from app.tests.utils.utils import gen_random_password, random_lower_string
from app.tests.utils.utils import random_email

from sqlalchemy.ext.asyncio.session import AsyncSession


@pytest.mark.asyncio
async def test_create_user(db: AsyncSession) -> models.User:
    rnd_str = random_lower_string()
    password = gen_random_password()
    user_in = schemas.UserCreate(
        email=f"{rnd_str}@gmail.com",
        username=rnd_str,
        password=password,
        password_confirm=password,
        full_name=fake.name(),
        age=random.randint(18, 25),
        phone="+7" + "".join(random.choice(string.digits) for _ in range(10)),
    )
    user = await crud.user.create(db, obj_in=user_in)
    return user


@pytest.mark.asyncio
async def test_get_users_superuser_me(
    client: AsyncClient,
    superuser_token_headers: Dict[str, str],
) -> None:
    r = await client.get(
        f"{get_app_settings().api_v1}/users/me",
        headers=superuser_token_headers,
    )
    current_user = r.json()
    assert current_user
    assert current_user["is_active"] is True
    assert current_user["email"] == get_app_settings().FIRST_SUPERUSER_EMAIL


@pytest.mark.asyncio
async def test_get_users_normal_user_me(
    client: AsyncClient,
    normal_user_token_headers: Dict[str, str],
) -> None:
    r = await client.get(
        f"{get_app_settings().api_v1}/users/me",
        headers=normal_user_token_headers,
    )
    current_user = r.json()
    assert current_user
    assert current_user["is_active"] is True
    assert current_user["email"] == get_app_settings().FIRST_SUPERUSER_EMAIL


@pytest.mark.asyncio
async def test_create_user_new_email(
    client: AsyncClient,
    superuser_token_headers: dict,
    db: AsyncSession,
) -> None:
    email = random_email()
    username = random_lower_string()
    password = gen_random_password()
    user_in = UserCreate(email=email, username=username, password=password, password_confirm=password,
                         role=UserRole.admin.name)
    r = await client.post(
        f"{get_app_settings().api_v1}/users/",
        headers=superuser_token_headers,
        json=user_in.dict(),
    )
    assert 200 <= r.status_code < 300
    created_user = r.json()
    user = await crud.user.get_by_email(db, email=email)
    assert user
    assert user.email == created_user["email"]


@pytest.mark.asyncio
async def test_get_existing_user(
    client: AsyncClient,
    superuser_token_headers: dict,
    db: AsyncSession,
) -> None:
    email = random_email()
    username = random_lower_string()
    password = gen_random_password()
    user_in = UserCreate(email=email, username=username, password=password, password_confirm=password,
                         role=UserRole.admin.name)
    user = await crud.user.create(db, obj_in=user_in)
    user_id = user.id
    r = await client.get(
        f"{get_app_settings().api_v1}/users/{user_id}",
        headers=superuser_token_headers,
    )
    assert 200 <= r.status_code < 300
    api_user = r.json()
    existing_user = await crud.user.get_by_email(db, email=email)
    assert existing_user
    assert existing_user.email == api_user["email"]


@pytest.mark.asyncio
async def test_create_user_existing_username(
    client: AsyncClient,
    superuser_token_headers: dict,
    db: AsyncSession,
) -> None:
    email = random_email()
    username = random_lower_string()
    password = gen_random_password()
    user_in = UserCreate(email=email, username=username, password=password, password_confirm=password,
                         role=UserRole.admin.name)
    await crud.user.create(db, obj_in=user_in)
    r = await client.post(
        f"{get_app_settings().api_v1}/users/",
        headers=superuser_token_headers,
        json=user_in.dict(),
    )
    created_user = r.json()
    assert r.status_code == 400
    assert "_id" not in created_user


@pytest.mark.asyncio
async def test_retrieve_users(
    client: AsyncClient,
    superuser_token_headers: dict,
    db: AsyncSession,
) -> None:
    email = random_email()
    username = random_lower_string()
    password = gen_random_password()
    user_in = UserCreate(email=email, username=username, password=password, password_confirm=password,
                         role=UserRole.admin.name)
    await crud.user.create(db, obj_in=user_in)

    email2 = random_email()
    username2 = random_lower_string()
    password2 = gen_random_password()
    user_in2 = UserCreate(email=email2, username=username2, password=password2, password_confirm=password2,
                          role=UserRole.admin.name)
    await crud.user.create(db, obj_in=user_in2)

    r = await client.get(
        f"{get_app_settings().api_v1}/users/",
        headers=superuser_token_headers,
    )
    all_users = r.json()

    assert len(all_users) > 1
    for item in all_users:
        assert "email" in item
