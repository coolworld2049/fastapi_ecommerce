from fastapi import FastAPI
from prisma import Prisma
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request

from store_service.middlewares.http import (
    add_process_time_header,
    catch_exceptions_middleware,
)
from store_service.api.api_v1.api import api_router
from store_service.core.config import get_app_settings


def get_application() -> FastAPI:
    get_app_settings().configure_logging()
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
        api_router,
        prefix=get_app_settings().api_perfix,
    )
    application.middleware("http")(add_process_time_header)
    application.middleware("http")(catch_exceptions_middleware)

    @application.on_event("startup")
    async def startup() -> None:
        await prisma.connect()

    @application.on_event("shutdown")
    async def shutdown() -> None:
        if prisma.is_connected():
            await prisma.disconnect()

    return application


app = get_application()
prisma = Prisma(auto_register=True)


@app.get("/")
async def root(request: Request):
    response = get_app_settings().templates.TemplateResponse(
        "/base/index.html",
        context={
            "app_name": app.title.replace("_", " "),  # noqa
            "prisma_studio_port": get_app_settings().PRISMA_STUDIO_PORT,
            "request": request,
            "proto": "http",
            "host": get_app_settings().DOMAIN,
            "port": get_app_settings().PORT,
            "openapi_path": f"{app.openapi_url}",  # noqa
        },
    )
    return response
