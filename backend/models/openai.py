from pydantic import BaseModel


class OpenAIRequest(BaseModel):
    skills: list[str]
    job: str


class OpenAIResponse(BaseModel):
    roadmap: str
