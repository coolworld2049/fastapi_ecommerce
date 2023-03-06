from datetime import datetime, timedelta
from typing import Union

from pydantic import AnyHttpUrl, BaseSettings, validator
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    api_prefix = "/api/v1"
    enable_rbac = True

    APP_NAME: str
    DEBUG: bool
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, list[str]]) -> Union[list[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
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

    @property
    def cart_expires_timestamp(self):
        expire = datetime.now() + timedelta(minutes=60)
        return expire

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
