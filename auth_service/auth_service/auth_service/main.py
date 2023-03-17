from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request

from auth_service.api.api_v1.api import api_router
from auth_service.api.errors.http_error import http_error_handler
from auth_service.api.errors.validation_error import http422_error_handler
from auth_service.core.config import get_app_settings
from auth_service.core.logger import configure_logging
from auth_service.db.init_db import init_db
from auth_service.db.session import engines
from auth_service.middlewares.http import (
    process_time_header_middleware,
    catch_exceptions_middleware,
    logger_middleware,
)

configure_logging(
    get_app_settings().LOGGING_LEVEL,
    access_log_path=get_app_settings().project_path,
)


def get_application() -> FastAPI:
    application = FastAPI(**get_app_settings().fastapi_kwargs)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=get_app_settings().BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        expose_headers=["Content-Range", "Range"],
        allow_headers=[
            "*",
            "Authorization",
            "Content-Type",
            "Content-Range",
            "Range",
        ],
    )
    application.include_router(
        api_router, prefix=get_app_settings().api_prefix
    )
    application.add_exception_handler(
        HTTPException,
        http_error_handler,
    )
    application.add_exception_handler(
        RequestValidationError, http422_error_handler
    )
    application.middleware("http")(process_time_header_middleware)
    application.middleware("http")(catch_exceptions_middleware)
    application.middleware("http")(logger_middleware)

    return application


app = get_application()


@app.on_event("startup")
async def startup():
    if get_app_settings().APP_ENV.name == "dev":
        await init_db()


@app.on_event("shutdown")
async def shutdown():
    [await x.dispose() for x in engines.values() if x]


@app.get("/")
async def root(request: Request):
    response = get_app_settings().templates.TemplateResponse(
        "/base/index.html",
        context={
            "app_name": app.title.replace("_", " "),  # noqa
            "request": request,
            "proto": "http",
            "host": get_app_settings().DOMAIN,
            "port": get_app_settings().PORT,
            "api_prefix": get_app_settings().api_prefix,
            "openapi_path": f"{app.openapi_url}",  # noqa
        },
    )
    return response
