from dependency_injector.wiring import Provide, inject

from dependencies import HHParser
from models.parser import HHParserResponse


class ParserApplication:

    @inject
    async def parse_hh_vacancy(
        self,
        country: str = 'volgograd',
        name: str = 'programmist',
        page_start: int = 0,
        page_end: int = 0,
        *,
        hh_parser: HHParser = Provide['hh_parser']
    ) -> list[HHParserResponse]:
        main_pages_data = []
        for page in range(page_start, page_end + 1):
            main_pages_data.append(await hh_parser.main_page_process(
                country,
                name,
                page
            ))
        vacancies = []
        for page, page_data in enumerate(main_pages_data, start=page_start):
            for url in page_data:
                vacancies.append(await hh_parser.sub_page_process(url))
        return vacancies
