import logging
import os
import pathlib
from typing import Any, Optional

from starlette.templating import Jinja2Templates

from store_service.core.settings.base import BaseAppSettings, AppEnvTypes


class AppSettings(BaseAppSettings):
    docs_url: str = "/docs"
    api_perfix: str = "/api/v1"
    openapi_prefix: str = ""
    openapi_url: str = f"{api_perfix}/openapi.json"
    redoc_url: str = "/redoc"
    title: str = os.getenv("APP_NAME")

    APP_NAME: str
    APP_VERSION: str = "0.0.0"
    APP_ENV: AppEnvTypes
    DEBUG: Optional[bool] = False

    DOMAIN: str
    PORT: int

    BACKEND_CORS_ORIGINS: list[str]
    JWT_ALGORITHM: str = "HS256"
    JWT_SECRET_KEY: str
    FIRST_SUPERUSER_EMAIL: str
    FIRST_SUPERUSER_PASSWORD: str

    MONGODB_URL: str
    AUTH_SERVICE_URL: str
    AUTH_SERVICE_LOGIN_URL: str

    PRISMA_STUDIO_PORT: int = 5555

    LOGGING_LEVEL: int = logging.INFO
    LOGGERS: tuple[str, str] = ("uvicorn.asgi", "uvicorn.access")
    LOG_FILE_MAX_BYTES = 314572800

    class Config:
        validate_assignment = True

    @property
    def fastapi_kwargs(self) -> dict[str, Any]:
        return {
            "debug": self.DEBUG,
            "docs_url": self.docs_url,
            "openapi_prefix": self.openapi_prefix,
            "openapi_url": self.openapi_url,
            "redoc_url": self.redoc_url,
            "title": self.title,
            "version": self.APP_VERSION,
        }

    @property
    def project_path(self):
        return pathlib.Path(__file__).parent.parent.parent.parent

    @property
    def project_templates_path(self):
        return pathlib.Path(__file__).parent.parent.parent / "templates"

    @property
    def templates(self):
        return Jinja2Templates(directory=self.project_templates_path)

    @property
    def auth_service_login_url(self):
        return self.AUTH_SERVICE_URL + self.AUTH_SERVICE_LOGIN_URL
