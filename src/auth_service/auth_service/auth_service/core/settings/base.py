import os
import pathlib
from enum import Enum

from dotenv import load_dotenv
from loguru import logger
from pydantic import BaseSettings

load_dotenv()


class AppEnvTypes(str, Enum):
    prod: str = "prod"
    dev: str = "dev"
    test: str = "test"


def load_env_files(app_env: AppEnvTypes):
    service_path = pathlib.Path(__file__).parent.parent.parent.parent.parent
    try:
        stage_env_path = pathlib.Path(f"{service_path / '.env'}.{app_env}")
        res = load_dotenv(stage_env_path, override=True)
        msg = f"load_dotenv {stage_env_path.parts[-1]} {res}"
        assert res, msg
        logger.info(msg)
    except AssertionError as ae:
        logger.warning(ae)


class BaseAppSettings(BaseSettings):
    APP_ENV: AppEnvTypes = os.getenv("APP_ENV")
    if APP_ENV == AppEnvTypes.dev:
        load_env_files(APP_ENV)
