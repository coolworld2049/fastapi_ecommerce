import logging
import sys
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler
from typing import Union

from dotenv import load_dotenv
from loguru import logger
from pydantic import BaseSettings, validator

from store_service.core.logging import InterceptHandler

load_dotenv()


class Settings(BaseSettings):
    api_prefix = "/api/v1"
    enable_rbac = True

    APP_NAME: str
    DEBUG: bool
    BACKEND_CORS_ORIGINS: list[str] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(
        cls, v: Union[str, list[str]]
    ) -> Union[list[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return list(filter(lambda x: x not in ["http://", "https://"], v))
        elif v in ["http://", "https://"]:
            raise
        raise ValueError(v)

    DOMAIN: str
    PORT: int
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    FIRST_SUPERUSER_USERNAME: str
    FIRST_SUPERUSER_EMAIL: str
    FIRST_SUPERUSER_PASSWORD: str
    MONGODB_URL: str
    AUTH_SERVICE_URL: str

    LOGGING_LEVEL: int = logging.INFO
    LOGGERS: tuple[str, str] = ("uvicorn.asgi", "uvicorn.access")
    LOG_FILE_MAX_BYTES = 314572800

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
                {"sink": sys.stdout, "level": self.LOGGING_LEVEL},
            ]
        )

    class Config:
        case_sensitive = True
        env_file = ".env.dev"


settings = Settings()
