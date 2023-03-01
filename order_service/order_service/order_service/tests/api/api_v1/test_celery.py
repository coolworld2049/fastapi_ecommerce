# from typing import Dict
#
# import pytest
# from httpx import AsyncClient
#
# from order_service.core.config import get_app_settings
#
#
# @pytest.mark.asyncio
# async def test_celery_worker_test(
#     client: AsyncClient,
#     superuser_token_headers: Dict[str, str],
# ) -> None:
#     data = {"msg": "tests"}
#     r = await client.post(
#         f"{get_app_settings().api_v1}/utils/tests-celery/",
#         json=data,
#         headers=superuser_token_headers,
#     )
#     response = r.json()
#     assert response["msg"] == "Word received"
