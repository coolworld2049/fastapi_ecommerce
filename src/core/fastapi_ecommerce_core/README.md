fastapi-ecommerce-core

* logger
  ```python
  from fastapi_ecommerce_core.logger.configure import configure_logging # noqa
  from fastapi_ecommerce_core.logger.middleware import LoguruLoggingMiddleware # noqa
  from loguru import logger # noqa

  configure_logging(
      get_app_settings().LOGGING_LEVEL,
      access_log_path="access.log",
      error_log_path="error.log",
  )
  application.middleware("http")(LoguruLoggingMiddleware())
  logger.info("")
  ```