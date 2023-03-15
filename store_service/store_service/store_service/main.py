from fastapi import FastAPI
from loguru import logger
from prisma import Prisma
from prisma.errors import PrismaError
from pydantic.error_wrappers import ValidationError
from starlette import status
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from store_service.api.api_v1.api import api_router
from store_service.core.config import get_app_settings


def get_application() -> FastAPI:
    application = FastAPI(**get_app_settings().fastapi_kwargs)

    get_app_settings().configure_logging()

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
        api_router, prefix=get_app_settings().api_perfix
    )

    async def catch_exceptions_middleware(request: Request, call_next):
        try:
            return await call_next(request)
        except ValidationError as ew:
            logger.error(ew.args)
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": ew.errors()},
            )
        except PrismaError as de:
            logger.error(de)
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": de.args},
            )
        except Exception as e:
            logger.error(e.args)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "INTERNAL_SERVER_ERROR"},
            )

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
        "/html/verification.html",
        context={
            "app_name": app.title.replace("_", " "),
            "prisma_studio_port": get_app_settings().PRISMA_STUDIO_PORT,
            "request": request,
            "proto": "http",
            "host": get_app_settings().DOMAIN,
            "port": get_app_settings().PORT,
            "openapi_path": f"{app.openapi_url}",
        },
    )
    return response
