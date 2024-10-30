from dependency_injector.wiring import inject, Provide

from dependencies.openai import OpenAIClient


class OpenAIApplication:
    @inject
    def get_completion(self, skills: list[str], job: str, client: OpenAIClient = Provide['openai_client']):
        return client.get_completion(skills, job)
