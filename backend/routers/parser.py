from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, Query

from applications import ParserApplication
from models.parser import HHParserResponse

parser_router = APIRouter(prefix="/parser", tags=["Parser"])


@parser_router.get("/hh_vacancy")
@inject
async def get_bert_embedding(
    country: str = 'volgograd',
    name: str = 'programmist',
    page_start: int = Query(default=0, ge=0),
    page_end: int = Query(default=0, ge=0),
    *,
    parser_application: ParserApplication = Depends(Provide['parser_application'])
) -> list[HHParserResponse]:
    return await parser_application.parse_hh_vacancy(country, name, page_start, page_end)


@parser_router.get("/hh_vacancy_process")
@inject
async def get_bert_embedding(
    country: str = 'volgograd',
    name: str = 'programmist',
    page_start: int = Query(default=0, ge=0),
    page_end: int = Query(default=0, ge=0),
    *,
    parser_application: ParserApplication = Depends(Provide['parser_application'])
) -> list[HHParserResponse]:
    return await parser_application.parse_and_process_hh_vacancy(country, name, page_start, page_end)
