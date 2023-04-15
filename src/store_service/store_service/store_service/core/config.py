from functools import lru_cache
from typing import Dict
from typing import Type

from store_service.core.settings.app import AppSettings
from store_service.core.settings.base import StageType
from store_service.core.settings.development import DevAppSettings
from store_service.core.settings.production import ProdAppSettings
from store_service.core.settings.test import TestAppSettings

environments: Dict[StageType, Type[AppSettings]] = {
    StageType.dev: DevAppSettings,
    StageType.prod: ProdAppSettings,
    StageType.test: TestAppSettings,
}


@lru_cache
def get_app_settings() -> AppSettings:
    STAGE: StageType = AppSettings().STAGE
    config = environments[STAGE]
    return config()
