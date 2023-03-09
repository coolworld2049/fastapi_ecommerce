import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from typing import Any

from loguru import logger

from auth_service.core.logging import InterceptHandler
from auth_service.core.settings.base import BaseAppSettings


class AppSettings(BaseAppSettings):
    docs_url: str = "/docs"
    api_v1: str = "/api/v1"
    openapi_prefix: str = ""
    openapi_url: str = f"{api_v1}/openapi.json"
    redoc_url: str = "/redoc"
    title: str = os.getenv("APP_NAME")
    version: str = "0.0.0"

    APP_NAME: str
    DEBUG: bool

    DOMAIN: str
    PORT: int

    BACKEND_CORS_ORIGINS: list[str]
    JWT_ALGORITHM: str
    JWT_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    FIRST_SUPERUSER_USERNAME: str
    FIRST_SUPERUSER_EMAIL: str
    FIRST_SUPERUSER_PASSWORD: str

    PG_HOST: str
    PG_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    PG_DRIVER: str = "asyncpg"

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
            "version": self.version,
        }

    @property
    def raw_postgres_dsn(self):
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.PG_HOST}:{self.PG_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def postgres_asyncpg_dsn(self):
        return self.raw_postgres_dsn.replace(
            "postgresql", f"postgresql+{self.PG_DRIVER}"
        )

    def configure_logging(self) -> None:
        logging.getLogger().handlers = [InterceptHandler()]
        for logger_name in self.LOGGERS:
            logging_logger = logging.getLogger(logger_name)
            logging_logger.handlers = [
                InterceptHandler(level=self.LOGGING_LEVEL),
                RotatingFileHandler(
                    "access.log",
                    maxBytes=self.LOG_FILE_MAX_BYTES,
                    backupCount=1,
                ),
            ]

        logger.configure(
            handlers=[
                {"sink": sys.stderr, "level": self.LOGGING_LEVEL},
            ]
        )
