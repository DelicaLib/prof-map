from pydantic import BaseModel


class Vacancy(BaseModel):
    id: int
    name: str
    hh_id: int | None
    skills: list[str]


class VacancyDescriptor(BaseModel):
    name: str
    hh_id: int | None
    skills: list[str]


class Exist(BaseModel):
    exist: bool
