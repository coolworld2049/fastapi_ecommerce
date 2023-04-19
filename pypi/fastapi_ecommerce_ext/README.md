```python
from auth_service.core.config import get_app_settings
from auth_service.core.logger import configure_logging
from loguru import logger

configure_logging(
    get_app_settings().LOGGING_LEVEL,
    access_log_path="access.log",
    error_log_path="error.log",
)

logger.info("")
```