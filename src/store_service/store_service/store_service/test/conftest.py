import asyncio

import aiohttp
import pytest
import pytest_asyncio
from httpx import AsyncClient
from loguru import logger

from store_service.core.config import get_app_settings


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    try:
        yield loop
    finally:
        loop.close()


@pytest_asyncio.fixture(scope="module")
async def store_service_client():
    from store_service.main import app

    async with AsyncClient(
        app=app,
        base_url=f"http://{get_app_settings().APP_HOST}:{get_app_settings().APP_PORT}",
    ) as c:
        yield c


@pytest_asyncio.fixture(scope="module")
async def auth_service_client():
    async with aiohttp.ClientSession(
        base_url=get_app_settings().AUTH_SERVICE_URL
    ) as session:
        try:
            await session.get("/")
        except Exception as e:
            logger.error(e)
        yield session


@pytest_asyncio.fixture(scope="module")
async def prisma_client():
    from store_service.main import prisma

    return prisma
