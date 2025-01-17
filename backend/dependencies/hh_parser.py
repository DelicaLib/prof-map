import asyncio
import re
from concurrent.futures import ThreadPoolExecutor
from functools import partial

from models.parser import HHParserResponse
from utils.bs4_utils import get_content


class HHParser:

    @staticmethod
    async def main_page_process(country: str, name: str, page: int) -> list[str]:
        url = f'https://{country}.hh.ru/search/vacancy?text={name}&page={page}'

        if country == 'moscow':
            url = f'https://hh.ru/search/vacancy?text={name}&page={page}'

        content_bs4 = await get_content(url)
        data = []
        if content_bs4:
            content_item_card = content_bs4.find_all('a', {'data-qa': 'serp-item__title'})
            for content in content_item_card:
                if 'href' in content.attrs:
                    data.append(content['href'])
        return data

    async def main_page_async(self, country: str, name: str, page_start: int, page_end: int) -> tuple[list[str]]:
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor(max_workers=min(5, abs(page_end - page_start) + 1)) as executor:
            tasks = [
                loop.run_in_executor(
                    executor,
                    partial(asyncio.run, self.main_page_process(country, name, page))
                )
                for page in range(page_start, page_end + 1)
            ]
            results = await asyncio.gather(*tasks)
            return results

    @staticmethod
    async def sub_page_process(url: str) -> HHParserResponse:
        content_bs4 = await get_content(url)
        attributes = {
            'title': {'tag': 'h1', 'params': {'data-qa': 'title'}},
            'salary': {'tag': 'span', 'params': {
                'data-qa': 'vacancy-salary-compensation-type-gross'}},
            'experience': {'tag': 'span', 'params': {'data-qa': 'vacancy-experience'}},
            'work_format': {'tag': 'p', 'params': {'class': 'vacancy-description-list-item',
                                                   'data-qa': 'vacancy-view-employment-mode'}},
            'description': {'tag': 'div', 'params': {'class': 'g-user-content', 'data-qa': 'vacancy-description'}},
            'skills': {'tag': 'li', 'params': {'data-qa': 'skills-element'}}
        }
        info_data = {'url': url}
        for name, attr in attributes.items():
            info_data[name] = None
            if name == 'skills':
                items = content_bs4.find_all(attr['tag'], attr['params'])
                if items:
                    skills = [item.text.strip() for item in items]
                    info_data[name] = skills
            else:
                item = content_bs4.find(attr['tag'], attr['params'])
                if item:
                    text = item.text.strip()
                    clean_text = re.sub(r'[\n\xa0\t]', '', text)
                    info_data[name] = clean_text
        return HHParserResponse(**info_data)

    async def sub_page_async(self, data_url_vacancies: list[str]) -> None:
        if len(data_url_vacancies) < 1:
            return None
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor(max_workers=min(5, len(data_url_vacancies))) as executor:
            tasks = [
                loop.run_in_executor(executor, partial(asyncio.run, self.sub_page_process(url)))
                for url in data_url_vacancies if "adsrv.hh.ru" not in url
            ]

            await asyncio.gather(*tasks)

