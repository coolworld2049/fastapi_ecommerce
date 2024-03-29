import json

import aiohttp
from fastapi import APIRouter
from starlette import status
from starlette.exceptions import HTTPException

from store_service.core.config import get_app_settings

router = APIRouter()


@router.get(
    "/store_service",
)
async def ping_auth_service():
    async with aiohttp.ClientSession(
        base_url=get_app_settings().AUTH_SERVICE_URL
    ) as session:
        response = {
            "store_service": {"url": get_app_settings().AUTH_SERVICE_URL},
        }
        try:
            resp = await session.get("/")
            assert resp.status in [404, 200]
            response["store_service"].update({"status": "alive"})
            return response
        except Exception:
            response["store_service"].update({"status": "unreachable"})
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=json.dumps(response),
            )
