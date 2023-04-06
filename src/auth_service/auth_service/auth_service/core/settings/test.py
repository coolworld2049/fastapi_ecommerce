import logging
import os

from auth_service.core.settings.app import AppSettings


class TestAppSettings(AppSettings):
    title: str = f"{os.getenv('APP_NAME')}_{os.getenv('APP_ENV')}"

    LOGGING_LEVEL: int = logging.DEBUG

    USE_RBAC = False
    USE_USER_CHECKS = False
    USE_EMAILS = False

    class Config(AppSettings.Config):
        env_file = ".env.auth_service"
