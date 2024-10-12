import logging
from contextlib import asynccontextmanager

import asyncpg

from dependencies.settings import Settings

LOGGER = logging.getLogger(__name__)


class LoggingConnectionProxy:
    def __init__(self, connection):
        self._connection = connection

    async def fetch(self, query, *args):
        LOGGER.debug(f"Executing fetch query: {query} with args: {args}")
        result = await self._connection.fetch(query, *args)
        LOGGER.debug(f"Fetch result rows count: {len(result)}")
        return result

    async def fetchval(self, query, *args):
        LOGGER.debug(f"Executing fetchval query: {query} with args: {args}")
        result = await self._connection.fetchval(query, *args)
        LOGGER.debug(f"Fetchval result: {result}")
        return result

    async def execute(self, query, *args):
        LOGGER.debug(f"Executing execute query: {query} with args: {args}")
        result = await self._connection.execute(query, *args)
        LOGGER.debug(f"Execute result: {result}")
        return result

    async def __aenter__(self):
        await self._connection.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._connection.__aexit__(exc_type, exc_val, exc_tb)

    def __getattr__(self, item):
        return getattr(self._connection, item)


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
        proxy_conn = LoggingConnectionProxy(conn)
        try:
            yield proxy_conn
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

    async def fetchval(self, query, *args):
        async with self._pool.acquire() as connection:
            LOGGER.debug(query)
            result_rows = await connection.fetchval(query, *args)
            LOGGER.debug(f"rows count: {len(result_rows)}")
            return result_rows

    async def execute(self, query, *args):
        async with self._pool.acquire() as connection:
            async with connection.transaction():
                LOGGER.debug(query)
                result_rows = await connection.execute(query, *args)
                LOGGER.debug(f"rows count: {len(result_rows)}")
                return result_rows
