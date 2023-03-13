from functools import lru_cache
from typing import Dict
from typing import Type

from store_service.core.settings.app import AppSettings
from store_service.core.settings.base import AppEnvTypes
from store_service.core.settings.development import DevAppSettings
from store_service.core.settings.production import ProdAppSettings
from store_service.core.settings.test import TestAppSettings

environments: Dict[AppEnvTypes, Type[AppSettings]] = {
    AppEnvTypes.dev: DevAppSettings,
    AppEnvTypes.prod: ProdAppSettings,
    AppEnvTypes.test: TestAppSettings,
}


@lru_cache
def get_app_settings() -> AppSettings:
    app_env: AppEnvTypes = AppSettings().APP_ENV
    config = environments[app_env]
    return config()
