from aiohttp import ClientSession
from loguru import logger

from store_service.schemas.user import User
from store_service.test.test_auth_service.utils import get_auth_service_token


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

        if resp.status != 200:
            raise AssertionError(resp.status)
        users = [User(**x) for x in data]
        logger.info(len(users))
        return users
