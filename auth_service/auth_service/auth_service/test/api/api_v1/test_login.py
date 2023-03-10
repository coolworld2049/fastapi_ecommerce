from typing import Dict

import pytest
from httpx import AsyncClient

from auth_service.core.config import get_app_settings


@pytest.mark.asyncio
async def test_get_access_token(client: AsyncClient) -> None:
    body = {
        "username": get_app_settings().FIRST_SUPERUSER_EMAIL,
        "password": get_app_settings().FIRST_SUPERUSER_PASSWORD,
    }
    r = await client.post(
        f"{get_app_settings().api_v1}/login/access-token", data=body
    )
    token = r.json()
    assert r.status_code == 200
    assert token
