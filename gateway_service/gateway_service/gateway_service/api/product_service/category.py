from fastapi import APIRouter
from fastapi_gateway import route
from starlette import status
from starlette.requests import Request
from starlette.responses import Response

from gateway_service.core.config import settings

# from store_service.models.category import (
#     CategoryCreate,
#     CategoryUpdate,
# )


router = APIRouter()


# noinspection PyUnusedLocal
@route(
    request_method=router.get,
    service_url=settings.PRODUCT_SERVICE_URL,
    gateway_path="/",
    service_path="/api/v1/categories/",
    status_code=status.HTTP_200_OK,
    override_headers=False,
    query_params=["skip", "limit"],
)
async def read_categories(
    request: Request, response: Response, skip: int = 0, limit: int = 10
):
    pass


# # noinspection PyUnusedLocal
# @route(
#     request_method=router.post,
#     service_url=settings.PRODUCT_SERVICE_URL,
#     gateway_path="/",
#     service_path="/api/v1/categories/",
#     status_code=status.HTTP_200_OK,
#     override_headers=False,
#     body_params=["category_in"],
# )
# async def create_category(
#     request: Request,
#     response: Response,
#     category_in: CategoryCreate,
# ):
#     pass
#
#
# # noinspection PyUnusedLocal
# @route(
#     request_method=router.put,
#     service_url=settings.PRODUCT_SERVICE_URL,
#     gateway_path="/{name}",
#     service_path="/api/v1/categories/{name}",
#     status_code=status.HTTP_200_OK,
#     override_headers=False,
#     query_params=["name"],
#     body_params=["category_in"],
# )
# async def update_category(
#     request: Request,
#     response: Response,
#     name: str,
#     category_in: CategoryUpdate,
# ):
#     pass
#
#
# # noinspection PyUnusedLocal
# @route(
#     request_method=router.delete,
#     service_url=settings.PRODUCT_SERVICE_URL,
#     gateway_path="/{name}",
#     service_path="/api/v1/categories/{name}",
#     status_code=status.HTTP_200_OK,
#     override_headers=False,
#     query_params=["name"],
# )
# async def delete_category(request: Request, response: Response, name: str):
#     pass
