import pytest
from aiohttp import ClientSession

from store_service.test.test_auth_service.utils import get_auth_service_token


@pytest.mark.asyncio
async def test_get_auth_service_token(auth_service_client: ClientSession):
    token = await get_auth_service_token(
        auth_service_client=auth_service_client
    )
    assert token
