import os
import pathlib
from enum import Enum

from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv()

load_dotenv(
    pathlib.Path(__file__).parent.parent.parent.parent.parent.parent / ".env"
)


class AppEnvTypes(str, Enum):
    prod: str = "prod"
    dev: str = "dev"
    test: str = "test"


class BaseAppSettings(BaseSettings):
    APP_ENV: AppEnvTypes = os.getenv("APP_ENV")

    class Config:
        env_file = ".env"
