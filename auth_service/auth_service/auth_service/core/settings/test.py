import logging
import os

from auth_service.core.settings.app import AppSettings


class TestAppSettings(AppSettings):
    title: str = f"{os.getenv('APP_NAME')}_{os.getenv('APP_ENV')}"

    DEBUG: bool = True
    LOGGING_LEVEL: int = logging.DEBUG

    class Config(AppSettings.Config):
        env_file = "test.env"
