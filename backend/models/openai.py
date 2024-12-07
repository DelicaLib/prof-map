from pydantic import BaseModel


class RoadMapRequest(BaseModel):
    skills: list[str]
    job: str


class LabelSkillsRequest(BaseModel):
    text: str


class OpenAIResponse(BaseModel):
    roadmap: dict
