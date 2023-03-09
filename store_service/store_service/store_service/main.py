from pathlib import Path

from fastapi import FastAPI
from prisma import Prisma
from prisma.errors import PrismaError
from pydantic.error_wrappers import ValidationError
from starlette import status
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.templating import Jinja2Templates
from loguru import logger

from store_service.api.api_v1.api import api_router
from store_service.core.config import settings

current_file = Path(__file__)
current_file_dir = current_file.parent
project_root = current_file_dir.parent
project_root_absolute = project_root.resolve()
project_templates_path = project_root_absolute / "store_service/templates"
project_templates_html_path = project_templates_path / "html/"

templates = Jinja2Templates(directory=project_templates_html_path)


def get_application() -> FastAPI:
    application = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

    settings.configure_logging()

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
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

    application.include_router(api_router, prefix=settings.api_prefix)

    async def catch_exceptions_middleware(request: Request, call_next):
        try:
            return await call_next(request)
        except ValidationError as ew:
            if request.app.debug:
                logger.exception(ew.args)
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": ew.errors()},
            )
        except PrismaError as de:
            if request.app.debug:
                logger.exception(de)
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": de.args},
            )
        except Exception as e:
            logger.error(e.args)
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            try:
                resp = JSONResponse(
                    status_code=status_code,
                    content={"detail": e.args},
                )
            except TypeError:
                resp = Response(status_code=status_code)
            return resp

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

prisma = Prisma(auto_register=True, log_queries=app.debug)


@app.get("/")
async def root(request: Request):
    response = templates.TemplateResponse(
        "index.html",
        context={
            "app_name": app.title.replace("_", " "),
            "request": request,
            "proto": "http",
            "host": settings.DOMAIN,
            "port": settings.PORT,
            "openapi_path": f"{app.openapi_url}",
        },
    )
    return response
