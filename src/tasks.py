import asyncio

import aiohttp
from bs4 import BeautifulSoup


async def certificate_taxi():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://pro.yandex.ru/ru-ru/moskva/knowledge-base/taxi/common/parks') as resp:
            html_code: str = await resp.text()

    soup = BeautifulSoup(html_code,'lxml')

    for req in soup.select("div.accordion_accordion__7KkXQ"):
        company: str = str(req.select_one("p.body2").string)
        phone: str = str(req.select("p.body2.icon-list-item_text__jP3Nc")[1].string)
        addres: str = str(req.select("p.body2.icon-list-item_text__jP3Nc")[2].string)
        print(company, ' + ', addres, ' + ', phone)


#asyncio.run(certificate_taxi())
