import asyncio

import aiohttp
import pytest
import pytest_asyncio
from httpx import AsyncClient
from loguru import logger

from store_service.core.config import get_app_settings


@pytest.fixture(scope="session")
def event_loop():
    return asyncio.get_event_loop()


@pytest_asyncio.fixture(scope="module")
async def store_service_client():
    from store_service.main import app

    async with AsyncClient(
        app=app,
        base_url=f"http://{get_app_settings().DOMAIN}:{get_app_settings().PORT}",
    ) as c:
        yield c


@pytest_asyncio.fixture(scope="module")
async def auth_service_client():
    async with aiohttp.ClientSession(
        base_url=get_app_settings().AUTH_SERVICE_URL
    ) as session:
        try:
            resp = await session.get("/")
        except Exception as e:
            logger.error(e)
            raise
        yield session


@pytest_asyncio.fixture(scope="module")
async def prisma_client():
    from store_service.main import prisma

    return prisma
