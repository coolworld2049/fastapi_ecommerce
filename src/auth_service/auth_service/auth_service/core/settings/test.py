import logging
import os

from auth_service.core.settings.app import AppSettings


class TestAppSettings(AppSettings):
    title: str = f"{os.getenv('APP_NAME')}_{os.getenv('APP_ENV')}"

    LOGGING_LEVEL: int = logging.DEBUG

    TEST_USE_RBAC = False
    TEST_USE_USER_CHECKS = False
    TEST_USE_EMAILS = False

    class Config(AppSettings.Config):
        env_file = ".env"
