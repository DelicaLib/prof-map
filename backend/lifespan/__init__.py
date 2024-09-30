import asyncio
import logging
from contextlib import asynccontextmanager

from dependency_injector.wiring import inject, Provide
from fastapi import FastAPI

from dependencies.postgres.pool import PostgresPool

LOGGER = logging.getLogger(__name__)


@inject
async def _ping_db(pool: PostgresPool = Provide['db_pool']):
    while True:
        try:
            result = await pool.fetch("SELECT 1;")
        except Exception as e:
            LOGGER.exception(f"Database is not responding: {e}")
        await asyncio.sleep(5)


@asynccontextmanager
async def lifespan(app: FastAPI, *, pool: PostgresPool = Provide['db_pool']):
    try:
        await pool.connect()
        LOGGER.info("Connected to database")
    except Exception as e:
        LOGGER.exception(f"Failed to connect to database: {e}")
        return
    task = asyncio.create_task(_ping_db())

    yield

    task.cancel()
    await pool.disconnect()
    LOGGER.info("Disconnected to database")
