from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, Query, BackgroundTasks

from applications import ParserApplication
from models.parser import HHParserResponse, HHParserResponseWithBDModel

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
    wait: bool = Query(default=True),
        *,
    background_tasks: BackgroundTasks,
    parser_application: ParserApplication = Depends(Provide['parser_application'])
) -> list[HHParserResponseWithBDModel]:
    if not wait:
        background_tasks.add_task(parser_application.parse_and_process_hh_vacancy, country, name, page_start, page_end)
        return []
    else:
        return await parser_application.parse_and_process_hh_vacancy(country, name, page_start, page_end)
