from datetime import datetime, timedelta
from typing import Union

from dotenv import load_dotenv
from pydantic import BaseSettings, validator

load_dotenv()


class Settings(BaseSettings):
    api_prefix = "/api/v1"
    enable_rbac = True

    APP_NAME: str
    DEBUG: bool
    BACKEND_CORS_ORIGINS: list[str] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, list[str]]) -> Union[list[str], str]:
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
    DATABASE_URL: str
    AUTH_SERVICE_API: str = "http://127.0.0.1:8001/api/v1/login/access-token"

    @property
    def cart_expires_timestamp(self):
        expire = datetime.now() + timedelta(minutes=60)
        return expire

    class Config:
        case_sensitive = True
        env_file = ".env.dev"


settings = Settings()
