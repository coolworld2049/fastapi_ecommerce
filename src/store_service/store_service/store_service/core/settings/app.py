import logging
import pathlib
from typing import Any, Optional

from pydantic import validator

from store_service.core.settings.base import BaseAppSettings, StageType


class AppSettings(BaseAppSettings):
    api_prefix: str = "/api/v1"
    docs_url: str = f"{api_prefix}/docs"
    openapi_prefix: str = f""
    openapi_url: str = f"{api_prefix}/openapi.json"
    redoc_url: str = f"{api_prefix}/redoc"

    APP_NAME: Optional[str] = 'store-service'
    APP_HOST: Optional[str] = "localhost"
    APP_PORT: Optional[int] = 8082
    APP_MODULE: Optional[str] = "store_service.main:app"
    STAGE: StageType
    APP_VERSION: Optional[str] = "latest"

    APP_BACKEND_CORS_ORIGINS: Optional[list[str]] = ["*"]
    JWT_ALGORITHM: Optional[str] = "HS256"
    JWT_SECRET_KEY: str
    FIRST_SUPERUSER_EMAIL: str
    FIRST_SUPERUSER_PASSWORD: str

    MONGODB_URL: str
    AUTH_SERVICE_URL: str
    AUTH_SERVICE_LOGIN_PATH: str

    LOGGING_LEVEL: Optional[int] = logging.INFO

    @validator("APP_BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | list[str]) -> str | list[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    class Config:
        validate_assignment = True

    @property
    def fastapi_kwargs(self) -> dict[str, Any]:
        title = (
            self.APP_NAME
            + f"{f'_{self.STAGE.name}' if self.STAGE != StageType.prod else ''}"
        )
        return {
            "debug": True if self.LOGGING_LEVEL == logging.DEBUG else False,
            "docs_url": self.docs_url,
            "openapi_prefix": self.openapi_prefix,
            "openapi_url": self.openapi_url,
            "redoc_url": self.redoc_url,
            "title": title,
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
        return self.AUTH_SERVICE_URL + self.AUTH_SERVICE_LOGIN_PATH
