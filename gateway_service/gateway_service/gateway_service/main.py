from pathlib import Path

from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from starlette.requests import Request
from starlette.templating import Jinja2Templates

from gateway_service.api.api import api_router
from gateway_service.core.config import settings

current_file = Path(__file__)
current_file_dir = current_file.parent
project_root = current_file_dir.parent
project_root_absolute = project_root.resolve()
project_templates_path = project_root_absolute / "gateway_service/templates"
project_templates_html_path = project_templates_path / "html/"

templates = Jinja2Templates(directory=project_templates_html_path)


def get_application() -> FastAPI:
    application = FastAPI(title=settings.APP_NAME)

    application.include_router(api_router)
    return application


app = get_application()

oauth2schema = OAuth2PasswordBearer(
    tokenUrl="/api/v1/login/access-token", scheme_name="JWT"
)


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
