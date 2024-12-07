from pydantic import BaseModel


class TextRequest(BaseModel):
    text: str


class ToBertEmbeddingResponse(BaseModel):
    embedding: list


class SkillsList(BaseModel):
    skills: list
