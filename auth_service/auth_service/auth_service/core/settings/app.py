import logging
import os
import pathlib
import sys
from logging.handlers import RotatingFileHandler
from typing import Any

from loguru import logger
from pydantic import EmailStr
from pydantic.networks import PostgresDsn
from starlette.templating import Jinja2Templates

from auth_service.core.logging import InterceptHandler
from auth_service.core.settings.base import BaseAppSettings


class AppSettings(BaseAppSettings):
    docs_url: str = "/docs"
    api_prefix: str = "/api/v1"
    openapi_prefix: str = ""
    openapi_url: str = f"/openapi.json"
    redoc_url: str = "/redoc"
    title: str = os.getenv("APP_NAME")
    VERSION: str = "0.0.0"

    APP_NAME: str
    DEBUG: bool

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
    PG_PORT: int
    PG_PORT_SLAVE_1: int
    PG_PORT_SLAVE_2: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    EMAIL_HOST: str
    EMAIL_PORT: int
    EMAIL_USERNAME: str
    EMAIL_PASSWORD: str
    EMAIL_FROM: EmailStr

    LOGGING_LEVEL: int = logging.INFO
    LOGGERS: tuple = ("uvicorn.asgi", "uvicorn.access")
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
            "version": self.VERSION,
        }

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
            host=str(self.PG_HOST),
            port=str(self.PG_PORT),
            path=f"/{self.POSTGRES_DB}",
        )
        return dsn

    @property
    def postgres_asyncpg_master_dsn(self) -> str:
        dsn = PostgresDsn.build(
            scheme="postgresql+psycopg",
            user=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=str(self.PG_HOST),
            port=str(self.PG_PORT),
            path=f"/{self.POSTGRES_DB}",
        )
        return dsn

    @property
    def postgres_slave_ports(self):
        return self.PG_PORT_SLAVE_1, self.PG_PORT_SLAVE_2

    def get_postgres_asyncpg_slave_dsn(self, num: int) -> str:
        if (
            not len(self.postgres_slave_ports) > 0
            and not len(self.postgres_slave_ports) >= num
        ):
            raise
        dsn = PostgresDsn.build(
            scheme="postgresql+psycopg",
            user=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=str(self.PG_HOST),
            port=str(self.postgres_slave_ports[num - 1]),
            path=f"/{self.POSTGRES_DB}",
        )
        return dsn

    @property
    def project_templates_path(self):
        return pathlib.Path(__file__).parent.parent.parent / "templates"

    @property
    def templates(self) -> Jinja2Templates:
        return Jinja2Templates(directory=self.project_templates_path)

    def configure_logging(self) -> None:
        logging.getLogger().handlers = [InterceptHandler()]
        for logger_name in self.LOGGERS:
            logging_logger = logging.getLogger(logger_name)
            logging_logger.handlers = [
                InterceptHandler(level=self.LOGGING_LEVEL),
                RotatingFileHandler(
                    f"access.log",
                    maxBytes=self.LOG_FILE_MAX_BYTES,
                    backupCount=1,
                ),
            ]
        logger.configure(
            handlers=[
                {"sink": sys.stdout, "level": self.LOGGING_LEVEL},
            ]
        )
