import pytest
from aiohttp import ClientSession

from store_service.core.config import get_app_settings


async def get_auth_service_token(auth_service_client: ClientSession) -> str:
    headers = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    body = {
        "username": get_app_settings().FIRST_SUPERUSER_EMAIL,
        "password": get_app_settings().FIRST_SUPERUSER_PASSWORD,
    }
    async with auth_service_client.post(
        "/api/v1/login/access-token", headers=headers, data=body
    ) as resp:
        data = await resp.json()
        token = data.get("access_token")
        assert token, data
        return token


@pytest.mark.asyncio
async def test_get_auth_service_token(auth_service_client: ClientSession):
    token = await get_auth_service_token(
        auth_service_client=auth_service_client
    )
    assert token
