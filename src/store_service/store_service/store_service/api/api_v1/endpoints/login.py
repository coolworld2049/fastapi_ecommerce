from typing import Any

import aiohttp
from fastapi import APIRouter
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm

from store_service.core.config import get_app_settings

router = APIRouter()


@router.post("/login")
async def login_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm),
) -> Any:
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    body = {
        "username": form_data.username,
        "password": form_data.password,
    }
    async with aiohttp.ClientSession(
        base_url=get_app_settings().AUTH_SERVICE_URL
    ) as session:
        resp = await session.post(
            get_app_settings().AUTH_SERVICE_LOGIN_PATH,
            headers=headers,
            data=body,
        )
        data: dict = await resp.json()
        assert data.get("access_token"), data
        return data
