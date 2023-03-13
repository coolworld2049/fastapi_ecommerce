import pytest
from aiohttp import ClientSession

from store_service.schemas.user import User
from store_service.test.auth_service.utils import get_auth_service_token


async def get_users(
    count=100, *, auth_service_client: ClientSession
) -> list[User]:
    token = await get_auth_service_token(auth_service_client)
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {token}",
    }
    async with auth_service_client.get(
        f"""/api/v1/users/?range=[0, {count}]&sort=["id", "ASC"]""",
        headers=headers,
    ) as resp:
        data = await resp.json()
        assert resp.status == 200
        return [User(**x) for x in data]


@pytest.mark.asyncio
async def test_get_users(auth_service_client: ClientSession):
    users = await get_users(count=5, auth_service_client=auth_service_client)
    assert users
