import asyncio

import aiohttp
import pytest
import pytest_asyncio
from loguru import logger
from prisma import Prisma

from store_service.core.config import get_app_settings


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    try:
        yield loop
    finally:
        loop.close()


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
    test_prisma = Prisma(auto_register=True)
    return test_prisma
