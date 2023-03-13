import random
import string
from typing import Dict

from httpx import AsyncClient
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.core.config import get_app_settings


def random_lower_string(n=32) -> str:
    return "".join(random.choices(string.ascii_lowercase, k=n))


def random_email(st: str = None) -> EmailStr:
    return EmailStr(
        f"{random_lower_string() if not st else f'{st}_{random_lower_string(6)}'}@gmail.com"
    )


def gen_random_password():
    length = 10
    return (
        f"{''.join(random.choice(string.ascii_letters) for _ in range(length)).capitalize()}"
        f"{random.choice(string.ascii_uppercase)}"
        f"{random.randint(0, 9)}"
        f"{random.choice('@$!%*?&')}"
    )


async def get_superuser_token_headers(
    client: AsyncClient, db: AsyncSession
) -> Dict[str, str]:
    body = {
        "username": get_app_settings().FIRST_SUPERUSER_EMAIL,
        "password": get_app_settings().FIRST_SUPERUSER_PASSWORD,
    }
    r = await client.post(
        f"{get_app_settings().api_prefix}/login/access-token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=body,
    )
    a_token = r.json().get("access_token")
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers
