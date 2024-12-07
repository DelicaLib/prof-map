from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends

from applications.openai import OpenAIApplication
from models.openai import RoadMapRequest, OpenAIResponse, LabelSkillsRequest

openai_router = APIRouter(prefix="/openai", tags=["OpenAI"])


@openai_router.post("/gpt_completion")
@inject
async def get_completion(
    request: RoadMapRequest,
    *,
    openai_application: OpenAIApplication = Depends(Provide['openai_application'])
) -> OpenAIResponse:
    result = await openai_application.get_roadmap(request)
    return result
