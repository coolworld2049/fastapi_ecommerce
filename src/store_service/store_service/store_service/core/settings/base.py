import os
import pathlib
from enum import Enum

from dotenv import load_dotenv
from loguru import logger
from pydantic import BaseSettings

load_dotenv()


class StageType(str, Enum):
    dev: str = "dev"
    test: str = "test"
    stag: str = "stag"
    prod: str = "prod"


def load_env_files(stage: StageType):
    service_path = pathlib.Path(__file__).parent.parent.parent.parent.parent
    try:
        stage_env_path = pathlib.Path(f"{service_path / '.env'}.{stage}")
        res = load_dotenv(stage_env_path, override=True)
        msg = f"load_dotenv {stage_env_path.parts[-1]} {res}"
        assert res, msg
        logger.info(msg)
    except AssertionError as ae:
        logger.warning(ae)


class BaseAppSettings(BaseSettings):
    STAGE: StageType = os.getenv("STAGE")
    if STAGE == StageType.dev:
        load_env_files(STAGE)
