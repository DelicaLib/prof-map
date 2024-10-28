import asyncio
import logging
from contextlib import asynccontextmanager

from dependency_injector.wiring import inject, Provide
from fastapi import FastAPI

from applications import ServiceApplication
from dependencies.postgres.pool import PostgresPool

LOGGER = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(
        app: FastAPI,
        *,
        pool: PostgresPool = Provide['db_pool'],
        service_application: ServiceApplication = Provide['service_application']
):
    try:
        await pool.connect()
        LOGGER.info("Connected to database")
    except Exception as e:
        LOGGER.exception(f"Failed to connect to database: {e}")
        return

    await service_application.prepare_bert()
    task = asyncio.create_task(service_application.ping_db())

    yield

    task.cancel()
    await pool.disconnect()
    LOGGER.info("Disconnected to database")
