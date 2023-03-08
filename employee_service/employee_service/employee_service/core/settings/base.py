import os
from enum import Enum

from dotenv import load_dotenv
from pydantic import BaseSettings


load_dotenv()


class AppEnvTypes(str, Enum):
    prod: str = "mongodb_cluster_prod"
    dev: str = "mongodb_cluster_dev"
    test: str = "test"


class BaseAppSettings(BaseSettings):
    APP_ENV: AppEnvTypes = os.getenv("APP_ENV", AppEnvTypes.dev.name)

    class Config:
        env_file = ".env.mongodb_cluster_dev"
