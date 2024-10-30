from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends

from applications.openai import OpenAIApplication
from models.openai import OpenAIRequest, OpenAIResponse

openai = APIRouter(prefix="/openai")


@openai.post("/gpt_completion")
@inject
async def get_completion(request: OpenAIRequest,
                         *,
                         openai_application: OpenAIApplication = Depends(Provide['openai_application'])
                         ) -> OpenAIResponse:
    result = await openai_application.get_completion(request.skills, request.job)
    return OpenAIResponse(roadmap=result)
