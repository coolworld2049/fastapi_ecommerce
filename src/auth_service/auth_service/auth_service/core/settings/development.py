import logging
import os

from auth_service.core.settings.app import AppSettings


class DevAppSettings(AppSettings):
    title: str = f"{os.getenv('APP_NAME')}_{os.getenv('APP_ENV')}"

    LOGGING_LEVEL: int = logging.DEBUG

    class Config(AppSettings.Config):
        env_file = ".env.auth_service"
