import logging

from store_service.core.settings.app import AppSettings


class DevAppSettings(AppSettings):
    LOGGING_LEVEL: int = logging.DEBUG
