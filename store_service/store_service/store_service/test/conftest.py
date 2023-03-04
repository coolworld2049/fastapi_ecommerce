import asyncio

import pytest
import pytest_asyncio


@pytest.fixture(scope="session")
def event_loop():
    return asyncio.get_event_loop()


@pytest_asyncio.fixture(scope="module")
async def prisma_client():
    from store_service.main import prisma

    return prisma

