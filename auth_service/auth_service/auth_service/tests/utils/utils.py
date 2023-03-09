import random
import string
from typing import Dict

from httpx import AsyncClient
from pydantic import EmailStr

from auth_service.api.dependencies.auth import oauth2Scheme
from auth_service.core.config import get_app_settings


def random_lower_string(n=32) -> str:
    return "".join(random.choices(string.ascii_lowercase, k=n))


def random_email() -> EmailStr:
    return EmailStr(f"{random_lower_string()}@gmail.com")


def gen_random_password():
    length = 10
    return (
        f"{''.join(random.choice(string.ascii_letters) for _ in range(length)).capitalize()}"
        f"{random.choice(string.ascii_uppercase)}"
        f"{random.randint(0, 9)}"
        f"{random.choice('@$!%*?&')}"
    )


async def get_superuser_token_headers(client: AsyncClient) -> Dict[str, str]:
    login_data = {
        "username": get_app_settings().FIRST_SUPERUSER_EMAIL,
        "password": get_app_settings().FIRST_SUPERUSER_PASSWORD,
    }
    r = await client.post(
        f"{get_app_settings().api_v1}/login/access-token", data=login_data
    )
    a_token = r.cookies.get(oauth2Scheme.token_name)
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers
