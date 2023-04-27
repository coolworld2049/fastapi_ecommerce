import asyncio
import logging

from loguru import logger
from sqlalchemy import text
from tenacity import after_log
from tenacity import before_log
from tenacity import retry
from tenacity import stop_after_attempt
from tenacity import wait_fixed

from db.session import async_engines

max_tries = 60 * 2  # target_db minute
wait_seconds = 1


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.ERROR),
    after=after_log(logger, logging.WARNING),
)
async def init() -> None:
    eng = async_engines.get_master()
    try:
        async with eng.begin() as conn:
            await conn.execute(text("select source_db"))
        logger.info(f"repl_type: master, url: {eng.url}")
    except ConnectionRefusedError as ex:
        logger.error(
            f"repl_type: master, url: {eng.url}, {ex.__class__.__name__} {ex}"
        )


def main() -> None:
    logger.info("Initializing service")
    asyncio.run(init())
    logger.info("Service finished initializing")


if __name__ == "__main__":
    main()
