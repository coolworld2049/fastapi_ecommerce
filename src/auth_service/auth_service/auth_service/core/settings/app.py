import logging
import os
import pathlib
from typing import Any, Optional

from pydantic.networks import PostgresDsn
from starlette.templating import Jinja2Templates

from auth_service.core.settings.base import BaseAppSettings, AppEnvTypes


class AppSettings(BaseAppSettings):
    docs_url: str = "/docs"
    api_prefix: str = "/api/v1"
    openapi_prefix: str = ""
    openapi_url: str = f"/openapi.json"
    redoc_url: str = "/redoc"

    TEST_USE_RBAC = True
    TEST_USE_USER_CHECKS = True
    TEST_USE_EMAILS = True

    APP_NAME: str
    APP_HOST: str
    APP_PORT: str
    APP_ENV: AppEnvTypes
    APP_VERSION: str = "latest"

    BACKEND_CORS_ORIGINS: list[str]
    JWT_ALGORITHM: str
    JWT_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    FIRST_SUPERUSER_EMAIL: str
    FIRST_SUPERUSER_PASSWORD: str
    FIRST_SUPERUSER_FULLNAME: str
    FIRST_SUPERUSER_USERNAME: str

    POSTGRESQL_MASTER_HOST: str
    POSTGRESQL_SLAVE_HOST: str
    POSTGRESQL_MASTER_PORT: int
    POSTGRESQL_SLAVE_PORT: int
    POSTGRESQL_DATABASE: str
    POSTGRESQL_USERNAME: str
    POSTGRESQL_PASSWORD: str

    SMTP_HOST: Optional[str]
    SMTP_PORT: Optional[int]
    SMTP_USERNAME: Optional[str]
    SMTP_PASSWORD: Optional[str]
    SMTP_FROM: Optional[str]

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
            "title": self.APP_NAME,
            "version": self.APP_VERSION,
        }

    @property
    def project_path(self):
        return pathlib.Path(__file__).parent.parent.parent

    @property
    def logs_path(self):
        return self.project_path / ".logs"

    @property
    def jinja_templates(self) -> Jinja2Templates:
        return Jinja2Templates(directory=self.project_path / "templates")

    @property
    def base_url(self):
        proto = "https" if os.getenv("APP_ENV") == AppEnvTypes.prod else "http"
        return f"{proto}://{self.APP_HOST}"

    @property
    def postgres_master_dsn(self) -> str:
        dsn = PostgresDsn.build(
            scheme="postgresql",
            user=self.POSTGRESQL_USERNAME,
            password=self.POSTGRESQL_PASSWORD,
            host=self.POSTGRESQL_MASTER_HOST,
            port=str(self.POSTGRESQL_MASTER_PORT),
            path=f"/{self.POSTGRESQL_DATABASE}",
        )
        return dsn

    @property
    def postgres_asyncpg_master(self) -> str:
        return self.postgres_master_dsn.replace(
            "postgresql", "postgresql+asyncpg"
        )

    @property
    def postgres_asyncpg_slaves(self) -> str:
        dsn = PostgresDsn.build(
            scheme="postgresql+asyncpg",
            user=self.POSTGRESQL_USERNAME,
            password=self.POSTGRESQL_PASSWORD,
            host=self.POSTGRESQL_SLAVE_HOST,
            port=str(self.POSTGRESQL_SLAVE_PORT),
            path=f"/{self.POSTGRESQL_DATABASE}",
        )
        return dsn
