from pathlib import Path

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.docs import get_swagger_ui_html
from loguru import logger
from starlette.exceptions import HTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from order_service.api.api_v1.api import api_router
from order_service.api.errors.http_error import http_error_handler
from order_service.api.errors.validation_error import http422_error_handler
from order_service.api.openapi import custom_openapi
from order_service.api.openapi import use_route_names_as_operation_ids
from order_service.core.config import get_app_settings
from order_service.db.init_db import init_db
from order_service.db.session import SessionLocal, engine

current_file = Path(__file__)
current_file_dir = current_file.parent
project_root = current_file_dir.parent
project_root_absolute = project_root.resolve()
project_templates_path = project_root_absolute / "order_service/templates"
project_templates_html_path = project_templates_path / "html/"

templates = Jinja2Templates(directory=project_templates_html_path)


def get_application() -> FastAPI:
    get_app_settings().configure_logging()

    application = FastAPI(**get_app_settings().fastapi_kwargs)

    application.include_router(api_router, prefix=get_app_settings().api_v1)
    custom_openapi(application)
    use_route_names_as_operation_ids(application)

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

    # application.state.engine = engine
    # application.state.session_maker = SessionLocal

    # if application.debug:
    #     application.middleware("http")(add_process_time_header)
    #
    # if not application.debug:
    #     application.middleware("http")(catch_exceptions_middleware)

    application.mount(
        "/templates",
        StaticFiles(directory=project_templates_path),
        name="templates",
    )

    return application


app = get_application()


@app.on_event("startup")
async def startup():
    logger.opt(colors=True).warning("<m>Application startup!</m>")
    if get_app_settings().APP_ENV.name == "dev":
        await init_db()


@app.on_event("shutdown")
async def shutdown():
    await SessionLocal.close_all()
    logger.opt(colors=True).warning("all sessionmaker session closed")
    await engine.dispose()
    logger.opt(colors=True).warning("engine disposed")
    logger.opt(colors=True).warning("<y>Application shutdown!</y>")


@app.get("/")
async def root(request: Request):
    response = templates.TemplateResponse(
        "index.html",
        context={
            "app_name": app.title,
            "request": request,
            "proto": "http",
            "host": get_app_settings().DOMAIN,
            "port": get_app_settings().PORT,
            "openapi_path": f"{app.openapi_url}",
        },
    )
    return response


@app.get("/docs/dark-theme", include_in_schema=False)
async def custom_swagger_ui_html_cdn():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Swagger UI",
        swagger_css_url="https://cdn.jsdelivr.net/gh/Itz-fork/Fastapi-Swagger-UI-Dark/assets/swagger_ui_dark.css",
    )
