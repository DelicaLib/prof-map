from openai import OpenAI

from dependencies.settings import Settings


class OpenAIClient:
    def __init__(self, settings: Settings):
        self.client = OpenAI(
            api_key=settings.openai.gpt_token,
            base_url="https://api.proxyapi.ru/openai/v1"
        )

    async def get_roadmap(self, skills: list[str], job: str) -> dict:
        completion = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user",
                 "content": f"Я хочу составить roadmap для {job}.\
                 У меня уже есть следующие навыки: {skills}\
                 Пожалуйста, помоги мне с шагами, которые нужно предпринять для достижения успеха в этой профессии.\
                 Укажи ключевые навыки, которые нужно развивать, рекомендованные курсы или ресурсы для обучения, а также"
                 f" возможные карьерные пути и перспективы роста.\
                 Также включи примерные временные рамки для каждого этапа."}

            ]
        )
        return completion.choices[0].message.dict()

    async def generate_road_map_text(self, text: str) -> dict:
        completion = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user",
                 "content": f""""""}

            ]
        )
        return completion.choices[0].message.dict()
