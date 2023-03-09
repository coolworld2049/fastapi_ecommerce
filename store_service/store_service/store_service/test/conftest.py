import asyncio

import pytest
import pytest_asyncio
from httpx import AsyncClient

from store_service.core.config import settings


@pytest.fixture(scope="session")
def event_loop():
    return asyncio.get_event_loop()


@pytest_asyncio.fixture(scope="module")
async def client():
    from store_service.main import app

    async with AsyncClient(
            app=app,
            base_url=f"http://{settings.DOMAIN}:{settings.PORT}",
    ) as c:
        yield c


@pytest_asyncio.fixture(scope="module")
async def prisma_client():
    from store_service.main import prisma

    return prisma
