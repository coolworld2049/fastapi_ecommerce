from fastapi import APIRouter
from fastapi_gateway import route
from starlette import status
from starlette.requests import Request
from starlette.responses import Response

from gateway_service.core.config import settings

# from store_service.models.product import ProductCreate, ProductUpdate

router = APIRouter()


# noinspection PyUnusedLocal
@route(
    request_method=router.get,
    service_url=settings.PRODUCT_SERVICE_URL,
    gateway_path="/",
    service_path="/api/v1/products/",
    status_code=status.HTTP_200_OK,
    override_headers=False,
    query_params=["skip", "limit"],
)
async def read_products(
    request: Request, response: Response, skip: int = 0, limit: int = 10
):
    pass


#
# # noinspection PyUnusedLocal
# @route(
#     request_method=router.post,
#     service_url=settings.PRODUCT_SERVICE_URL,
#     gateway_path="/",
#     service_path="/api/v1/products/",
#     status_code=status.HTTP_200_OK,
#     override_headers=False,
#     body_params=["product_in"],
# )
# async def create_product(
#     request: Request,
#     response: Response,
#     product_in: ProductCreate,
# ):
#     pass
#
#
# # noinspection PyUnusedLocal
# @route(
#     request_method=router.put,
#     service_url=settings.PRODUCT_SERVICE_URL,
#     gateway_path="/{product_title}",
#     service_path="/api/v1/products/{product_title}",
#     status_code=status.HTTP_200_OK,
#     override_headers=False,
#     query_params=["product_title"],
#     body_params=["product_in"],
# )
# async def update_product(
#     request: Request,
#     response: Response,
#     product_title: str,
#     product_in: ProductUpdate,
# ):
#     pass
#
#
# # noinspection PyUnusedLocal
# @route(
#     request_method=router.delete,
#     service_url=settings.PRODUCT_SERVICE_URL,
#     gateway_path="/product_title}",
#     service_path="/api/v1/products/{product_title}",
#     status_code=status.HTTP_200_OK,
#     override_headers=False,
#     query_params=["product_title"],
# )
# async def delete_product(
#     request: Request, response: Response, product_title: str
# ):
#     pass
