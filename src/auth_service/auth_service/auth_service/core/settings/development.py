import logging

from auth_service.core.settings.app import AppSettings


class DevAppSettings(AppSettings):
    LOGGING_LEVEL: int = logging.DEBUG
