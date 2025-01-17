import asyncpg

from models.vacancy import VacancyDescriptor


class VacancyDAO:
    def __init__(self, connection: asyncpg.Connection):
        self._connection = connection

    async def get_skill(self, skill_name: str) -> str | None:
        skill_name = await self._connection.fetchval("""
            SELECT name 
            FROM skill
            WHERE name=$1
        """, skill_name)
        return skill_name

    async def get_skills(self, skill_names: list[str]) -> list[int | None]:
        skill_names_result = await self._connection.fetch("""
            SELECT id, name 
            FROM skill
            WHERE name = ANY($1)
        """, skill_names)
        skill_names_dict: dict[str, int] = {row["name"]: row["id"] for row in skill_names_result}

        return [skill_names_dict.get(skill_name) for skill_name in skill_names]

    async def insert_new_skills(self, skill_names: list[str]) -> list[int]:
        if len(skill_names) == 0:
            return []
        insert_values = ",".join([f"(${i})" for i in range(1, len(skill_names) + 1)])
        new_skills = await self._connection.fetch(f"""
            INSERT INTO skill (name) 
            VALUES {insert_values}
            RETURNING id
        """, *skill_names)
        return [row["id"] for row in new_skills]

    async def get_hh_vacancies(self, hh_ids: list[int]) -> list[int | None]:
        query_result = await self._connection.fetch("""
                    SELECT id, hh_id
                    FROM vacancy
                    WHERE hh_id = ANY($1)
                """, hh_ids)
        vacancies_ids_dict: dict[int, int] = {row["hh_id"]: row["id"] for row in query_result}

        return [vacancies_ids_dict.get(hh_id) for hh_id in hh_ids]

    async def insert_new_vacancies(self, vacancies: list[VacancyDescriptor]) -> list[int]:
        if len(vacancies) == 0:
            return []
        insert_values = ",".join([f"(${i}, ${i + len(vacancies)})" for i in range(1, len(vacancies) + 1)])
        names: list[str] = []
        hh_ids: list[str | None] = []
        for vacancy in vacancies:
            names.append(vacancy.name)
            hh_ids.append(vacancy.hh_id)
        new_vacancies = await self._connection.fetch(f"""
            INSERT INTO vacancy (name, hh_id) 
            VALUES {insert_values}
            RETURNING id
        """, *(names + hh_ids))
        return [row["id"] for row in new_vacancies]

    async def insert_vacancy_to_skill(self, vacancies_ids: list[int], skills_ids: list[list[int]]) -> None:
        if len(vacancies_ids) == 0 or len(skills_ids) != len(vacancies_ids):
            return
        vacancies_ids_insert_list: list[int] = []
        skills_ids_insert_list: list[int] = []
        for idx, vacancy_id in enumerate(vacancies_ids, 0):
            for skill_id in skills_ids[idx]:
                vacancies_ids_insert_list.append(vacancy_id)
                skills_ids_insert_list.append(skill_id)
        if len(vacancies_ids_insert_list) == 0 or len(skills_ids_insert_list) == 0:
            return
        insert_values = ",".join(
            [
                f"(${i}, ${i + len(vacancies_ids_insert_list)})"
                for i in range(1, len(vacancies_ids_insert_list) + 1)
            ]
        )
        await self._connection.fetch(f"""
            INSERT INTO vacancy_skill (vacancy_id, skill_id)
            VALUES {insert_values}
        """, *(vacancies_ids_insert_list + skills_ids_insert_list))
