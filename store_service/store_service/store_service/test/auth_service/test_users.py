import pytest
from httpx import AsyncClient

from store_service.schemas.user import User
from store_service.test.auth_service.utils import get_auth_service_token


async def get_users(
    count=100, *, auth_service_client: AsyncClient
) -> list[User]:
    token = await get_auth_service_token(auth_service_client)
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {token}",
    }
    resp = await auth_service_client.get(
        f"""/api/v1/users/?range=[0, {count}]&sort=["id", "ASC"]""",
        headers=headers,
    )
    assert resp.status_code == 200
    return [User(**x) for x in resp.json()]


@pytest.mark.asyncio
async def test_get_users(auth_service_client: AsyncClient):
    users = await get_users(count=5, auth_service_client=auth_service_client)
    assert users
