from datetime import datetime, timedelta
from typing import List, Union

from dotenv import load_dotenv
from pydantic import BaseSettings, validator

load_dotenv()


class Settings(BaseSettings):
    api_prefix = "/api/v1"

    APP_NAME: str
    BACKEND_CORS_ORIGINS: str

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(
        cls, v: Union[str, List[str]]
    ) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    MONGODB_URL: str
    DOMAIN: str
    PORT: int

    JWT_ALGORITHM: str
    JWT_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    FIRST_SUPERUSER_USERNAME: str
    FIRST_SUPERUSER_EMAIL: str
    FIRST_SUPERUSER_PASSWORD: str

    @property
    def cart_expires_timestamp(self):
        expire = datetime.now() + timedelta(minutes=60)
        return expire

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
