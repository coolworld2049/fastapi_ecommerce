import logging
import os
import pathlib
from typing import Any

from store_service.core.settings.base import BaseAppSettings, AppEnvTypes


class AppSettings(BaseAppSettings):
    docs_url: str = "/docs"
    api_perfix: str = "/api/v1"
    openapi_prefix: str = ""
    openapi_url: str = f"{api_perfix}/openapi.json"
    redoc_url: str = "/redoc"
    title: str = os.getenv("APP_NAME")

    APP_NAME: str
    APP_HOST: str
    APP_PORT: int
    APP_ENV: AppEnvTypes
    APP_VERSION: str = "latest"

    BACKEND_CORS_ORIGINS: list[str]
    JWT_ALGORITHM: str = "HS256"
    JWT_SECRET_KEY: str
    FIRST_SUPERUSER_EMAIL: str
    FIRST_SUPERUSER_PASSWORD: str

    MONGODB_URL: str
    AUTH_SERVICE_URL: str
    AUTH_SERVICE_LOGIN_URL: str

    LOGGING_LEVEL: int = logging.INFO

    class Config:
        validate_assignment = True

    @property
    def fastapi_kwargs(self) -> dict[str, Any]:
        return {
            "debug": True if self.LOGGING_LEVEL == logging.DEBUG else False,
            "docs_url": self.docs_url,
            "openapi_prefix": self.openapi_prefix,
            "openapi_url": self.openapi_url,
            "redoc_url": self.redoc_url,
            "title": self.title,
            "version": self.APP_VERSION,
        }

    @property
    def project_path(self):
        return pathlib.Path(__file__).parent.parent.parent

    @property
    def logs_path(self):
        return self.project_path / ".logs"

    @property
    def auth_service_login_url(self):
        return self.AUTH_SERVICE_URL + self.AUTH_SERVICE_LOGIN_URL
