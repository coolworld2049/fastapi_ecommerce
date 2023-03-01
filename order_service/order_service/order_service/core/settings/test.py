import logging
import os

from order_service.core.settings.app import AppSettings


class TestAppSettings(AppSettings):
    title: str = f"{os.getenv('APP_NAME')}_{os.getenv('APP_ENV')}"

    DEBUG: bool = True
    JWT_SECRET_KEY: str
    LOGGING_LEVEL: int = logging.DEBUG

    class Config(AppSettings.Config):
        env_file = ".env"
