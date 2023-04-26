import logging

from auth_service.core.settings.app import AppSettings


class TestAppSettings(AppSettings):
    LOGGING_LEVEL: int = logging.DEBUG

    USE_RBAC = False
    USE_USER_CHECKS = False
    USE_EMAILS = False

    PROFILE_QUERY_MODE = True
