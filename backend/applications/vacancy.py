import logging

from dependency_injector.wiring import inject, Provide

from dao.vacancy import VacancyDAO
from dependencies.postgres import PostgresPool
from models.base import ListModel
from models.vacancy import VacancyDescriptor, Vacancy

LOGGER = logging.getLogger(__name__)


class VacancyApplication:
    def __init__(self):
        pass

    @inject
    async def check_skill_exist(
        self,
        skill: str,
        *,
        pool: PostgresPool = Provide["db_pool"]
    ) -> bool:
        async with pool.acquire() as conn:
            exist_skill = await VacancyDAO(conn).get_skill(skill)
        return exist_skill is not None

    @inject
    async def check_some_skills_exist(
        self,
        skills: ListModel[str],
        *,
        pool: PostgresPool = Provide["db_pool"]
    ) -> list[bool]:
        async with pool.acquire() as conn:
            exist_skills = await VacancyDAO(conn).get_skills(skills.items)
        return [name is not None for name in exist_skills]

    @inject
    async def add_no_exist_skills(
        self,
        skills: ListModel[str],
        *,
        pool: PostgresPool = Provide["db_pool"]
    ) -> list[int]:
        async with pool.acquire() as conn:
            async with conn.transaction():
                vacancy_dao = VacancyDAO(conn)
                exist_skills = await vacancy_dao.get_skills(skills.items)
                no_exist_skills = [skills.items[idx] for idx, id_ in enumerate(exist_skills, 0) if id_ is None]
                new_skills_ids = await vacancy_dao.insert_new_skills(no_exist_skills)
        i = 0
        for idx, skill in enumerate(exist_skills, 0):
            if skill is None:
                exist_skills[idx] = new_skills_ids[i]
                i += 1
        return exist_skills

    @inject
    async def add_no_exist_vacancies(
        self,
        vacancies_descriptors: list[VacancyDescriptor],
        *,
        pool: PostgresPool = Provide["db_pool"]
    ) -> list[Vacancy]:
        hh_ids = [vacancy.hh_id for vacancy in vacancies_descriptors]

        async with pool.acquire() as conn:
            async with conn.transaction():
                vacancy_dao = VacancyDAO(conn)
                exist_vacancy_ids = await vacancy_dao.get_hh_vacancies(hh_ids)
                no_exist_vacancies = []
                for idx, vacancy in enumerate(vacancies_descriptors, 0):
                    if exist_vacancy_ids[idx] is None:
                        no_exist_vacancies.append(vacancy)
                all_skills: set[str] = set()
                for no_exist_vacancy in no_exist_vacancies:
                    all_skills.update(no_exist_vacancy.skills)
                all_skills_list = list(all_skills)
                skills_ids = await self.add_no_exist_skills(ListModel[str](items=all_skills_list))
                skill_to_id: dict[str, int] = {
                    skill_name: skill_id
                    for skill_name, skill_id in zip(all_skills_list, skills_ids)
                }

                new_vacancy_ids = await vacancy_dao.insert_new_vacancies(no_exist_vacancies)
                await vacancy_dao.insert_vacancy_to_skill(
                    new_vacancy_ids,
                    [
                        [
                            skill_to_id[skill_name]
                            for skill_name in vacancy.skills
                        ]
                        for vacancy in no_exist_vacancies
                    ]
                )

        no_exist_idx = 0
        result_vacancies = []
        for idx, vacancy in enumerate(vacancies_descriptors, 0):
            cur_vacancy = Vacancy(
                    id=0,
                    name=vacancy.name,
                    hh_id=vacancy.hh_id,
                    skills=vacancy.skills
                )
            if exist_vacancy_ids[idx] is None:
                cur_vacancy.id = new_vacancy_ids[no_exist_idx]
                no_exist_idx += 1
            else:
                cur_vacancy.id = exist_vacancy_ids[idx]
            result_vacancies.append(cur_vacancy)

        return result_vacancies
