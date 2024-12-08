from fastapi import FastAPI
from dependency_injector import providers
from dependency_injector.containers import DeclarativeContainer

from app import create_app
from applications import ServiceApplication, ParserApplication, BertApplication, OpenAIApplication, RoBertaApplication
from dependencies import HHParser
from dependencies.openai import OpenAIClient
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

    hh_parser: HHParser = providers.Singleton(HHParser)

    service_application: ServiceApplication = providers.Singleton(ServiceApplication)
    bert_application: BertApplication = providers.Singleton(BertApplication, settings=settings)
    roberta_application: RoBertaApplication = providers.Singleton(RoBertaApplication, settings=settings)
    parser_application: ParserApplication = providers.Singleton(ParserApplication)
    openai_client: OpenAIClient = providers.Singleton(OpenAIClient, settings=settings)
    openai_application: OpenAIApplication = providers.Singleton(OpenAIApplication)
