from auth_service.core.settings.app import AppSettings


class ProdAppSettings(AppSettings):
    class Config(AppSettings().Config):
        env_file = ".env"
