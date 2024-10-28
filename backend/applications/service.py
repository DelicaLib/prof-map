import asyncio
import logging

from dependency_injector.wiring import Provide, inject

from applications import BertApplication
from dependencies.postgres.pool import PostgresPool

LOGGER = logging.getLogger(__name__)


class ServiceApplication:

    @inject
    async def ping_db(self, pool: PostgresPool = Provide['db_pool']):
        while True:
            try:
                result = await pool.fetch("SELECT 1;")
            except Exception as e:
                LOGGER.exception(f"Database is not responding: {e}")
            await asyncio.sleep(5)

    @inject
    async def prepare_bert(self, bert_application: BertApplication = Provide['bert_application']):
        test_embedding = await bert_application.get_bert_embedding("test")
