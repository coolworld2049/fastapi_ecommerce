from httpx import AsyncClient

from store_service.core.config import settings


async def get_auth_service_token(auth_service_client: AsyncClient) -> str:
    headers = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    body = {
        "username": settings.FIRST_SUPERUSER_EMAIL,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    resp = await auth_service_client.post(
        "/api/v1/login/access-token", headers=headers, data=body
    )
    token = resp.json().get("access_token")
    assert token
    return token
