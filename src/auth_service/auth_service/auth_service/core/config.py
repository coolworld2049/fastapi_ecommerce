from functools import lru_cache
from typing import Dict
from typing import Type

from auth_service.core.settings.app import AppSettings
from auth_service.core.settings.base import StageType
from auth_service.core.settings.base import BaseAppSettings
from auth_service.core.settings.development import DevAppSettings
from auth_service.core.settings.production import ProdAppSettings
from auth_service.core.settings.test import TestAppSettings

environments: Dict[StageType, Type[AppSettings]] = {
    StageType.dev: DevAppSettings,
    StageType.prod: ProdAppSettings,
    StageType.test: TestAppSettings,
}


@lru_cache
def get_app_settings() -> AppSettings:
    stage: StageType = BaseAppSettings().STAGE
    config = environments[stage]
    return config()
