import asyncio
import logging

import aiohttp
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


LOGGER = logging.getLogger(__name__)


async def get_content(url, proxy=None) -> BeautifulSoup | None:
    error = 429
    cnt = 0

    while error == 429 and cnt < 5:
        cnt += 1
        headers = {
            "User-Agent": UserAgent().random
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, proxy=proxy if proxy else None, timeout=30) as response:
                    LOGGER.debug(f"Get response from {url}")
                    error = response.status
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        return soup
            await asyncio.sleep(10)

        except Exception as e:
            LOGGER.error(f"traceback.format_exc()\n\n{e}\n")
            return None
    return None
