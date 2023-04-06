import logging
import os
import pathlib
from typing import Any, Optional
from urllib.parse import urlparse

from pydantic.networks import PostgresDsn
from starlette.templating import Jinja2Templates

from auth_service.core.settings.base import BaseAppSettings, AppEnvTypes


class AppSettings(BaseAppSettings):
    docs_url: str = "/docs"
    api_prefix: str = "/api/v1"
    openapi_prefix: str = ""
    openapi_url: str = f"/openapi.json"
    redoc_url: str = "/redoc"

    USE_RBAC: Optional[bool] = True
    USE_USER_CHECKS: Optional[bool] = True
    USE_EMAILS: Optional[bool] = True if os.getenv("SMTP_PASSWORD") else False

    APP_NAME: str
    APP_HOST: str
    APP_PORT: int
    APP_ENV: AppEnvTypes
    APP_VERSION: str = "latest"

    APP_BACKEND_CORS_ORIGINS: list[str]
    JWT_ALGORITHM: str
    JWT_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    FIRST_SUPERUSER_EMAIL: str
    FIRST_SUPERUSER_PASSWORD: str
    FIRST_SUPERUSER_FULLNAME: str
    FIRST_SUPERUSER_USERNAME: str

    POSTGRESQL_MASTER_HOST: str
    POSTGRESQL_REPLICA_HOSTS: str
    POSTGRESQL_MASTER_PORT: int
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
    def postgres_replica_dsn(self) -> list[str]:
        def split_netloc():
            path = urlparse(
                self.POSTGRESQL_REPLICA_HOSTS, allow_fragments=True
            ).path
            path_arr = path.replace(" ", "").split(",")
            assert len(path_arr) > 0
            separated_str = [x.split(":") for x in path_arr if ":" in x]
            assert len(separated_str) > 0 and len(separated_str) == len(
                path_arr
            )
            return separated_str

        dsn_list = []
        for repl in split_netloc():
            dsn = PostgresDsn.build(
                scheme="postgresql",
                user=self.POSTGRESQL_USERNAME,
                password=self.POSTGRESQL_PASSWORD,
                host=repl[0],
                port=repl[1],
                path=f"/{self.POSTGRESQL_DATABASE}",
            )
            dsn_list.append(dsn)
        return dsn_list

    @property
    def postgres_asyncpg_master(self) -> str:
        return self.postgres_master_dsn.replace(
            "postgresql", "postgresql+asyncpg"
        )

    @property
    def postgres_asyncpg_replicas(self):
        return [
            x.replace("postgresql", "postgresql+asyncpg")
            for x in self.postgres_replica_dsn
        ]
