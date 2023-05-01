import logging

from store_service.core.settings.app import AppSettings


class TestAppSettings(AppSettings):
    LOGGING_LEVEL: int = logging.DEBUG
