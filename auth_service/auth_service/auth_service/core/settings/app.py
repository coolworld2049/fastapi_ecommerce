import logging
import os
import pathlib
from typing import Any, Optional

from loguru import logger
from pydantic import EmailStr
from pydantic.networks import PostgresDsn
from starlette.templating import Jinja2Templates

from auth_service.core.settings.base import BaseAppSettings, AppEnvTypes


class AppSettings(BaseAppSettings):
    docs_url: str = "/docs"
    api_prefix: str = "/api/v1"
    openapi_prefix: str = ""
    openapi_url: str = f"/openapi.json"
    redoc_url: str = "/redoc"
    title: str = os.getenv("APP_NAME")

    APP_NAME: str
    APP_ENV: AppEnvTypes
    APP_VERSION: str = "0.0.0"
    DEBUG: Optional[bool] = False

    DOMAIN: str
    PORT: int

    BACKEND_CORS_ORIGINS: list[str]
    JWT_ALGORITHM: str
    JWT_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    FIRST_SUPERUSER_EMAIL: str
    FIRST_SUPERUSER_PASSWORD: str
    FIRST_SUPERUSER_FULLNAME: str
    FIRST_SUPERUSER_USERNAME: str

    PG_HOST: str
    PG_PORT: str
    PG_HOST_SLAVE_1: Optional[str]
    PG_HOST_SLAVE_2: Optional[str]
    PG_PORT_SLAVE_1: Optional[str]
    PG_PORT_SLAVE_2: Optional[str]
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    EMAIL_HOST: Optional[str]
    EMAIL_PORT: Optional[int]
    EMAIL_USERNAME: Optional[str]
    EMAIL_PASSWORD: Optional[str]
    EMAIL_FROM: Optional[str] = os.getenv("EMAIL_USERNAME")

    LOGGING_LEVEL: int = logging.INFO
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
        return pathlib.Path(__file__).parent.parent.parent.parent.parent

    @property
    def project_templates_path(self):
        return pathlib.Path(__file__).parent.parent.parent / "templates"

    @property
    def templates(self) -> Jinja2Templates:
        return Jinja2Templates(directory=self.project_templates_path)

    @property
    def origin_url(self):
        proto = "https" if self.APP_ENV == "prod" else "http"
        return f"{proto}://{self.DOMAIN}:{self.PORT}{self.api_prefix}"

    @property
    def postgres_master_dsn(self) -> str:
        dsn = PostgresDsn.build(
            scheme="postgresql",
            user=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.PG_HOST,
            port=self.PG_PORT,
            path=f"/{self.POSTGRES_DB}",
        )
        return dsn

    @property
    def postgres_asyncpg_master_dsn(self) -> str:
        dsn = PostgresDsn.build(
            scheme="postgresql+asyncpg",
            user=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.PG_HOST,
            port=self.PG_PORT,
            path=f"/{self.POSTGRES_DB}",
        )
        return dsn

    @property
    def postgres_slave_addr(self):
        return (
            [
                {"host": self.PG_HOST_SLAVE_1, "port": self.PG_PORT_SLAVE_1},
                {"host": self.PG_HOST_SLAVE_2, "port": self.PG_PORT_SLAVE_2},
            ]
            if self.PG_HOST_SLAVE_2 or self.PG_HOST_SLAVE_2
            else []
        )

    def get_postgres_asyncpg_slave_dsn(self, num_slave: int) -> str | None:
        cond = (
            not len(self.postgres_slave_addr) > 0
            or not len(self.postgres_slave_addr) >= num_slave
            or num_slave <= 0
        )
        if cond:
            logger.warning(f"postgres_slave {num_slave} address not set")
            return None
        dsn = PostgresDsn.build(
            scheme="postgresql+asyncpg",
            user=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.postgres_slave_addr[num_slave - 1]["host"],
            port=self.postgres_slave_addr[num_slave - 1]["port"],
            path=f"/{self.POSTGRES_DB}",
        )
        return dsn
