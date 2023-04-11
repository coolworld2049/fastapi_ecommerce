from uuid import uuid4

from asgi_correlation_id import CorrelationIdMiddleware
from asgi_correlation_id.middleware import is_valid_uuid4
from fastapi import FastAPI
from loguru import logger
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request

from auth_service.api.api_v1.api import api_router
from auth_service.core.config import get_app_settings
from auth_service.core.logger import configure_logging
from auth_service.core.logging import LoguruLoggingMiddleware
from auth_service.core.settings.base import AppEnvTypes
from auth_service.db.init_db import init_db
from auth_service.db.session import async_engines, scoped_session

configure_logging(
    get_app_settings().LOGGING_LEVEL,
    access_log_path=get_app_settings().logs_path / "access.log",
    error_log_path=get_app_settings().logs_path / "error.log",
)

if get_app_settings().APP_ENV == AppEnvTypes.test:
    logger.warning(
        f"USE_RBAC={get_app_settings().USE_RBAC},"
        f" USE_USER_CHECKS={get_app_settings().USE_USER_CHECKS},"
        f" USE_EMAILS={get_app_settings().USE_EMAILS}"
    )


def get_application() -> FastAPI:
    application = FastAPI(**get_app_settings().fastapi_kwargs)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=get_app_settings().APP_BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        expose_headers=["*"],
    )
    application.include_router(
        api_router, prefix=get_app_settings().api_prefix
    )
    application.middleware("http")(LoguruLoggingMiddleware())
    application.add_middleware(
        CorrelationIdMiddleware,
        header_name="X-Request-ID",
        update_request_header=True,
        generator=lambda: uuid4().hex,
        validator=is_valid_uuid4,
        transformer=lambda a: a,
    )
    return application


app = get_application()


@app.on_event("startup")
async def startup():
    if get_app_settings().APP_ENV == AppEnvTypes.dev:
        await init_db()


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    async with scoped_session() as s:
        request.state.db = s
        response = await call_next(request)
    return response


@app.on_event("shutdown")
async def shutdown():
    [await x.dispose() for x in async_engines.get_all]
