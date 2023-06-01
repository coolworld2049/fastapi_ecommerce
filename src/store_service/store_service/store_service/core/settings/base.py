import os
import pathlib
from enum import Enum

from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv()


class StageType(str, Enum):
    dev: str = "dev"
    test: str = "test"
    staging: str = "staging"
    prod: str = "prod"


class BaseAppSettings(BaseSettings):
    STAGE: StageType = os.getenv("STAGE")
    if STAGE == StageType.dev:
        service_path = pathlib.Path(__file__).parent.parent.parent.parent.parent
        stage_env_path = pathlib.Path(f"{service_path / '.env'}.{STAGE}")
        load_dotenv(stage_env_path, override=True)
