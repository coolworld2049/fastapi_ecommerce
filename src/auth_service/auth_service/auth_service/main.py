from uuid import uuid4

from asgi_correlation_id import CorrelationIdMiddleware
from asgi_correlation_id.middleware import is_valid_uuid4
from fastapi import FastAPI
from fastapi_ecommerce_ext.logger.configure import configure_logging
from fastapi_ecommerce_ext.logger.middleware import LoguruLoggingMiddleware
from loguru import logger
from starlette.middleware.cors import CORSMiddleware

from auth_service.api.api_v1.api import api_router
from auth_service.core.config import get_app_settings
from auth_service.core.settings.base import StageType
from auth_service.db.init_db import init_db
from auth_service.db.session import async_engines, async_session

configure_logging(
    get_app_settings().LOGGING_LEVEL,
    access_log_path=get_app_settings().logs_path / "access.log",
)

logger.warning(
    f"USE_RBAC={get_app_settings().USE_RBAC},"
    f" USE_USER_CHECKS={get_app_settings().USE_USER_CHECKS},"
    f" USE_EMAILS={get_app_settings().USE_EMAILS}"
    f" PROFILE_QUERY_MODE={get_app_settings().PROFILE_QUERY_MODE}"
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
    if get_app_settings().STAGE != StageType.prod:
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
    if get_app_settings().STAGE != StageType.prod:
        async with async_session() as db:
            await init_db(db)


@app.on_event("shutdown")
async def shutdown():
    [await x.dispose() for x in async_engines.get_all]
