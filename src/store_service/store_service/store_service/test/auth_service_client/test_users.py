import pytest
from aiohttp import ClientSession
from loguru import logger

from store_service.schemas.user import User
from store_service.test.auth_service_client.test_login import (
    get_auth_service_token,
)


async def get_users(
    count=100, *, auth_service_client: ClientSession
) -> list[User]:
    token = await get_auth_service_token(auth_service_client)
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {token}",
    }
    async with auth_service_client.get(
        f"""/api/v1/users/?range=[0, {count}]""",
        headers=headers,
    ) as resp:
        data = await resp.json()

        if resp.status != 200:
            raise AssertionError(resp.status)
        users = [User(**x) for x in data]
        logger.info(len(users))
        return users


@pytest.mark.asyncio
async def test_get_users(auth_service_client: ClientSession):
    users = await get_users(count=5, auth_service_client=auth_service_client)
    assert len(users) >= 1
