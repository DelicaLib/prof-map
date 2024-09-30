from fastapi import FastAPI
from dependency_injector import providers
from dependency_injector.containers import DeclarativeContainer

from app import create_app
from dependencies.postgres.pool import PostgresPool
from dependencies.settings import Settings


class Container(DeclarativeContainer):

    raw_settings: dict = providers.Configuration()

    settings: Settings = providers.Singleton(
        lambda raw_settings: Settings(**raw_settings),
        raw_settings=raw_settings
    )

    db_pool: PostgresPool = providers.Singleton(PostgresPool, settings=settings)

    fastapi_app: FastAPI = providers.Singleton(create_app)
