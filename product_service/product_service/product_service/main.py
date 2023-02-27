from pathlib import Path

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.templating import Jinja2Templates

from product_service.api.api import api_router
from product_service.core.config import settings
from product_service.db.init_db import init_db

current_file = Path(__file__)
current_file_dir = current_file.parent
project_root = current_file_dir.parent
project_root_absolute = project_root.resolve()
project_templates_path = project_root_absolute / "product_service/templates"
project_templates_html_path = project_templates_path / "html/"

templates = Jinja2Templates(directory=project_templates_html_path)


def get_application() -> FastAPI:
    application = FastAPI(title=settings.APP_NAME)

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

    @application.on_event("startup")
    async def startup() -> None:
        await init_db()

    @application.on_event("shutdown")
    async def shutdown() -> None:
        pass

    return application


app = get_application()


@app.get("/")
async def root(request: Request):
    response = templates.TemplateResponse(
        "index.html",
        context={
            "app_name": app.title,
            "request": request,
            "proto": "http",
            "host": settings.DOMAIN,
            "port": settings.PORT,
            "openapi_path": f"{app.openapi_url}",
        },
    )
    return response
