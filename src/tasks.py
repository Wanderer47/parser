import aiohttp
import asyncio
from bs4 import BeautifulSoup


async def certificate_taxi():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://pro.yandex.ru/ru-ru/moskva/knowledge-base/taxi/common/parks') as resp:
            html_code: str = await resp.text()

    soup = BeautifulSoup(html_code)
    print(soup.find_all('span'))


asyncio.run(certificate_taxi())
