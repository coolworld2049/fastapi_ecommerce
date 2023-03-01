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

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
