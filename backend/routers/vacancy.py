from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends

from applications import VacancyApplication
from models.base import ListModel
from models.vacancy import Exist

vacancy_router = APIRouter(prefix="/vacancy", tags=["Vacancy"])


@vacancy_router.get("/check_exist_skill")
@inject
async def get_bert_embedding(
    skill: str,
    *,
    vacancy_application: VacancyApplication = Depends(Provide['vacancy_application'])
) -> Exist:
    result = await vacancy_application.check_skill_exist(skill=skill)
    return Exist(exist=result)


@vacancy_router.post("/check_exist_skills")
@inject
async def get_bert_embedding(
    skills: ListModel[str],
    *,
    vacancy_application: VacancyApplication = Depends(Provide['vacancy_application'])
) -> ListModel[bool]:
    result = await vacancy_application.check_some_skills_exist(skills)
    return ListModel[bool](items=result)


@vacancy_router.post("/add_noexist_skills")
@inject
async def get_bert_embedding(
    skills: ListModel[str],
    *,
    vacancy_application: VacancyApplication = Depends(Provide['vacancy_application'])
) -> ListModel[int]:
    result = await vacancy_application.add_no_exist_skills(skills)
    return ListModel[int](items=result)

