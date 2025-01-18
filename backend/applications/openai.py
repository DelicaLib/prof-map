from dependency_injector.wiring import inject, Provide

from dependencies.openai import OpenAIClient
from models.openai import OpenAIResponse, RoadMapRequest


class OpenAIApplication:
    @inject
    async def get_roadmap(
        self,
        request: RoadMapRequest,
        client: OpenAIClient = Provide['openai_client']
    ) -> OpenAIResponse:
        return OpenAIResponse(roadmap=await client.get_roadmap(request.skills))
