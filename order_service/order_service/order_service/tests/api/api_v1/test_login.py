from typing import Dict

import pytest
from httpx import AsyncClient

from order_service.core.config import get_app_settings


@pytest.mark.asyncio
async def test_get_access_token(client: AsyncClient) -> None:
    login_data = {
        "username": get_app_settings().FIRST_SUPERUSER_EMAIL,
        "password": get_app_settings().FIRST_SUPERUSER_PASSWORD,
    }
    r = await client.post(
        f"{get_app_settings().api_v1}/login/access-token", data=login_data
    )
    token = r.json()
    assert r.status_code == 200
    assert token


@pytest.mark.asyncio
async def test_use_access_token(
    client: AsyncClient,
    superuser_token_headers: Dict[str, str],
) -> None:
    r = await client.post(
        f"{get_app_settings().api_v1}/login/test-token",
        headers=superuser_token_headers,
    )
    result = r.json()
    assert r.status_code == 200

    assert "email" in result
