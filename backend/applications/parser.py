from logging import getLogger

from dependency_injector.wiring import Provide, inject

from applications import BertApplication
from applications.roberta import RoBertaApplication
from dependencies import HHParser
from models.language_model import SkillsList, ClusteredSkills
from models.parser import HHParserResponse

LOGGER = getLogger(__name__)


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

    @inject
    async def parse_and_process_hh_vacancy(
        self,
        country: str = 'volgograd',
        name: str = 'programmist',
        page_start: int = 0,
        page_end: int = 0,
        *,
        bert_application: BertApplication = Provide["bert_application"],
        roberta_application: RoBertaApplication = Provide["roberta_application"]
    ) -> list[HHParserResponse]:
        parsed_vacancy: list[HHParserResponse] = await self.parse_hh_vacancy(
            country,
            name,
            page_start,
            page_end
        )
        skills_list: list[SkillsList] = [
            await bert_application.get_skills_from_text(vacancy.description)
            for vacancy in parsed_vacancy
        ]

        all_skills: set[str] = set()

        for bert_skills, vacancy in zip(skills_list, parsed_vacancy):
            cur_skills: set[str] = set(vacancy.skills)
            cur_skills.update(bert_skills.skills)
            vacancy.skills = list(cur_skills)
            all_skills.update(cur_skills)

        clustered_skills: ClusteredSkills = await roberta_application.get_clustered_skills(list(all_skills))

        skill_to_label: dict[str, str] = {}
        for label, skills in clustered_skills.clustered_skills.items():
            for skill in skills:
                skill_to_label[skill] = label

        for vacancy in parsed_vacancy:
            cur_skills: set[str] = set()
            for skill in vacancy.skills:
                if len(skill) > 0:
                    cur_skills.add(skill_to_label[skill.lower().strip()])
            vacancy.skills = list(cur_skills)

        return parsed_vacancy
