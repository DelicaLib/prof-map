from pydantic import BaseModel


class TextRequest(BaseModel):
    text: str


class ToBertEmbeddingResponse(BaseModel):
    embedding: list


class ClusteredSkills(BaseModel):
    clustered_skills: dict[str, list[str]]
    combined_skills: list[str]


class SkillsListRequest(BaseModel):
    skills: list[str]


class SkillsList(BaseModel):
    skills: list[str]
    clustered: ClusteredSkills
