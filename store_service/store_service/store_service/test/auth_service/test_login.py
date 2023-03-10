import pytest
from httpx import AsyncClient

from store_service.test.auth_service.utils import get_auth_service_token


@pytest.mark.asyncio
async def test_get_auth_service_token(auth_service_client: AsyncClient):
    token = await get_auth_service_token(
        auth_service_client=auth_service_client
    )
    assert token
