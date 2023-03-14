from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from loguru import logger
from starlette.exceptions import HTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request

from auth_service.api.api_v1.api import api_router
from auth_service.api.errors.http_error import http_error_handler
from auth_service.api.errors.validation_error import http422_error_handler
from auth_service.core.config import get_app_settings
from auth_service.db.init_db import init_db
from auth_service.db.session import SessionLocal, engine
from auth_service.middlewares.http import (
    add_process_time_header,
    catch_exceptions_middleware,
)


def get_application() -> FastAPI:
    get_app_settings().configure_logging()

    application = FastAPI(**get_app_settings().fastapi_kwargs)

    application.include_router(
        api_router, prefix=get_app_settings().api_prefix
    )

    application.add_exception_handler(HTTPException, http_error_handler)
    application.add_exception_handler(
        RequestValidationError, http422_error_handler
    )

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

    application.middleware("http")(add_process_time_header)

    application.middleware("http")(catch_exceptions_middleware)

    return application


app = get_application()


@app.on_event("startup")
async def startup():
    if get_app_settings().APP_ENV.name == "dev":
        await init_db()


@app.on_event("shutdown")
async def shutdown():
    logger.info("Application shutdown!")
    await SessionLocal.close_all()
    await engine.dispose()


@app.get("/")
async def root(request: Request):
    response = get_app_settings().templates.TemplateResponse(
        "/html/index.html",
        context={
            "app_name": app.title.replace("_", " "),
            "request": request,
            "proto": "http",
            "host": get_app_settings().DOMAIN,
            "port": get_app_settings().PORT,
            "api_prefix": get_app_settings().api_prefix,
            "openapi_path": f"{app.openapi_url}",
        },
    )
    return response
