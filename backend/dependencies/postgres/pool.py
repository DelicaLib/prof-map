import logging
from contextlib import asynccontextmanager

import asyncpg

from dependencies.settings import Settings

LOGGER = logging.getLogger(__name__)


class PostgresPool:
    def __init__(self, settings: Settings):
        self._config = settings.postgres
        self._pool = None

    async def connect(self):
        self._pool = await asyncpg.create_pool(
            user=self._config.db_user,
            password=self._config.db_password,
            database=self._config.db_name,
            host=self._config.db_host,
            port=self._config.db_port
        )

    async def disconnect(self):
        if self._pool:
            await self._pool.close()

    @asynccontextmanager
    async def acquire(self):
        conn = await self._pool.acquire()
        try:
            yield conn
        finally:
            await self._pool.release(conn)

    async def release(self, connection):
        await self._pool.release(connection)

    async def fetch(self, query, *args):
        async with self._pool.acquire() as connection:
            LOGGER.debug(query)
            result_rows = await connection.fetch(query, *args)
            LOGGER.debug(f"rows count: {len(result_rows)}")
            return result_rows

    async def execute(self, query, *args):
        async with self._pool.acquire() as connection:
            async with connection.transaction():
                LOGGER.debug(query)
                result_rows = await connection.execute(query, *args)
                LOGGER.debug(f"rows count: {len(result_rows)}")
                return result_rows
