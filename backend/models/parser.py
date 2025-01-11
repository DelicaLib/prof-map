from pydantic import BaseModel, field_validator, model_validator
from pydantic_core.core_schema import ValidationInfo
from urllib.parse import urlparse

from models.vacancy import VacancyDescriptor, Vacancy


class HHParserResponse(BaseModel):
    url: str
    hh_id: int | None = None
    title: str
    salary: str | None
    experience: str | None
    work_format: str | None
    description: str
    skills: list[str]

    @model_validator(mode='before')
    @classmethod
    def _get_hh_id(cls, data):
        if isinstance(data, dict):
            if "url" in data:
                parsed_url = urlparse(data["url"])
                data["hh_id"] = int(parsed_url.path.split('/')[-1])
        return data

    @field_validator('skills', 'description', 'title', mode='before')
    @classmethod
    def _fields_empty_if_none(cls, v: list[str] | None | str, info: ValidationInfo) -> list[str] | str:
        if v is None:
            if info.field_name in ['description', 'title']:
                v = ''
            else:
                v = []
        return v

    def to_descriptor(self) -> VacancyDescriptor:
        return VacancyDescriptor(name=self.title, hh_id=self.hh_id, skills=self.skills)


class HHParserResponseWithBDModel(HHParserResponse):
    vacancy: Vacancy
