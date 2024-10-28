from pydantic import BaseModel, field_validator
from pydantic_core.core_schema import ValidationInfo


class HHParserResponse(BaseModel):
    url: str
    title: str
    salary: str | None
    experience: str | None
    work_format: str | None
    description: str
    skills: list[str]

    @field_validator('skills', 'description', 'title', mode='before')
    @classmethod
    def _fields_empty_if_none(cls, v: list[str] | None | str, info: ValidationInfo) -> list[str] | str:
        if v is None:
            if info.field_name in ['description', 'title']:
                v = ''
            else:
                v = []
        return v
