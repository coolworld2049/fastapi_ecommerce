from enum import Enum
from typing import Any

from loguru import logger
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine


class ReplicaType(str, Enum):
    master = "master"
    slave = "slave"


# noinspection PyUnusedLocal
class MasterSlaves:
    __slots__ = "engine",

    def __init__(self, master_url: str, slaves_url: str, *args, **kwargs):
        self.engine: dict[ReplicaType, AsyncEngine | tuple[AsyncEngine]] = {}
        self.engine.update(
            {ReplicaType.master: (create_async_engine(master_url, **kwargs), )}
        )
        self.engine.update(
            {
                ReplicaType.slave: (create_async_engine(slaves_url, **kwargs), )
                if slaves_url
                else []
            }
        )

    @property
    def get_all(self) -> tuple[Any, Any]:
        return (
            *self.engine[ReplicaType.master],
            *self.engine[ReplicaType.slave],
        )

    async def check_engines(self):
        for _type, _eng in self.engine.items():
            for i, eng in enumerate(_eng):
                try:
                    async with eng.begin() as conn:
                        await conn.execute(text("select 1"))
                    logger.info(f"engine_type: {_type.name}, url: {eng.url}")
                except ConnectionRefusedError as ex:
                    logger.error(
                        f"engine_type: {_type.name}, url: {eng.url}, {ex.__class__.__name__} {ex}"
                    )
