from logging import getLogger

from dependency_injector.wiring import Provide, inject

from applications.vacancy import VacancyApplication
from applications.bert import BertApplication
from applications.roberta import RoBertaApplication
from dependencies import HHParser
from models.language_model import SkillsList, ClusteredSkills
from models.parser import HHParserResponse, HHParserResponseWithBDModel

LOGGER = getLogger(__name__)


class ParserApplication:

    _BATCH_SIZE = 10

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
                if "adsrv.hh.ru" not in url:
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
        vacancy_application: VacancyApplication = Provide["vacancy_application"],
        roberta_application: RoBertaApplication = Provide["roberta_application"],
    ) -> list[HHParserResponseWithBDModel]:
        result_vacancies: list[HHParserResponseWithBDModel] = []

        for start in range(page_start, page_end + 1, self._BATCH_SIZE):
            end = min(start + self._BATCH_SIZE - 1, page_end)
            LOGGER.info(f"Started batch from page {start} to page {end}")
            raw_parsed_vacancy: list[HHParserResponse] = await self.parse_hh_vacancy(
                country,
                name,
                start,
                end
            )
            raw_parsed_vacancy = list({
                raw_vacancy.hh_id: raw_vacancy
                for raw_vacancy in raw_parsed_vacancy
            }.values())

            LOGGER.info(f"parsed {len(raw_parsed_vacancy)} vacancies from page {start}-{end}")
            skills_list: list[SkillsList] = [
                await bert_application.get_skills_from_text(vacancy.description)
                for vacancy in raw_parsed_vacancy
            ]

            all_skills: set[str] = set()

            for bert_skills, vacancy in zip(skills_list, raw_parsed_vacancy):
                cur_skills: set[str] = set(vacancy.skills)
                cur_skills.update(bert_skills.skills)
                vacancy.skills = list(cur_skills)
                all_skills.update(cur_skills)

            clustered_skills: ClusteredSkills = await roberta_application.get_clustered_skills(list(all_skills))

            skill_to_label: dict[str, str] = {}
            for label, skills in clustered_skills.clustered_skills.items():
                for skill in skills:
                    skill_to_label[skill] = await bert_application.normalize_word(label)

            for vacancy in raw_parsed_vacancy:
                cur_skills: set[str] = set()
                for skill in vacancy.skills:
                    if len(skill) > 0:
                        cur_skills.add(skill_to_label[skill.lower().strip()])
                vacancy.skills = list(cur_skills)\

            parsed_vacancy: list[HHParserResponse] = []
            for raw_vacancy in raw_parsed_vacancy:
                if len(raw_vacancy.skills) != 0:
                    parsed_vacancy.append(raw_vacancy)

            new_vacancies = await vacancy_application.add_no_exist_vacancies(
                [vacancy.to_descriptor() for vacancy in parsed_vacancy]
            )
            raw_vacancies: list[dict] = [cur_parsed_vacancy.dict() for cur_parsed_vacancy in parsed_vacancy]
            for idx, raw_vacancy in enumerate(raw_vacancies, 0):
                raw_vacancy["vacancy"] = new_vacancies[idx]
                result_vacancies.append(HHParserResponseWithBDModel(**raw_vacancy))

        LOGGER.info(f"Total parsed {len(result_vacancies)}")

        return result_vacancies
