from openai import OpenAI


class OpenAIClient:
    def __init__(self):
        self.client = OpenAI()

    async def get_completion(self, skills: list[str], job: str):
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
        return completion.choices[0].message
