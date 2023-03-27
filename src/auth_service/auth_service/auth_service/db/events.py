import time

from loguru import logger
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncEngine

from auth_service.core.config import get_app_settings
from auth_service.core.settings.base import AppEnvTypes

if get_app_settings().APP_ENV == AppEnvTypes.dev:

    @event.listens_for(AsyncEngine, "before_cursor_execute")
    def before_cursor_execute(
        conn, cursor, statement, parameters, context, executemany
    ):
        conn.info.setdefault("query_start_time", []).append(time.time())
        logger.debug(
            f"Start Query: {statement}",
        )

    @event.listens_for(AsyncEngine, "after_cursor_execute")
    def after_cursor_execute(
        conn, cursor, statement, parameters, context, executemany
    ):
        total = time.time() - conn.info["query_start_time"].pop(-1)
        logger.debug("Query Complete!")
        logger.debug(f"Total Time: {total:0.4f}")
