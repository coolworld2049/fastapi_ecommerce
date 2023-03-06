import asyncio
from os import environ
from typing import Dict, AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from employee_service.core.config import get_app_settings
from employee_service.db.session import SessionLocal
from employee_service.main import app
from employee_service.tests.utils.user import authentication_token_from_email
from employee_service.tests.utils.utils import get_superuser_token_headers

environ["APP_ENV"] = "test"


@pytest.fixture(scope="session")
def event_loop():
    return asyncio.get_event_loop()


@pytest_asyncio.fixture(scope="module")
async def client() -> AsyncGenerator:
    async with AsyncClient(
        app=app,
        base_url=f"http://{get_app_settings().DOMAIN}:{get_app_settings().PORT}",
    ) as c:
        yield c


@pytest_asyncio.fixture(scope="session")
async def db() -> AsyncGenerator:
    session = SessionLocal()
    try:
        yield session
    finally:
        await session.close()


# noinspection PyShadowingNames
@pytest_asyncio.fixture(scope="module")
async def superuser_token_headers(client: AsyncClient) -> Dict[str, str]:
    return await get_superuser_token_headers(client)


# noinspection PyShadowingNames
@pytest_asyncio.fixture(scope="module")
async def normal_user_token_headers(
    client: AsyncClient, db: AsyncSession
) -> Dict[str, str]:
    return await authentication_token_from_email(
        client=client,
        email=get_app_settings().FIRST_SUPERUSER_EMAIL,
        db=db,
    )
