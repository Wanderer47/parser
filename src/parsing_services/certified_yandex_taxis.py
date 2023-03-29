from os import environ

import aiohttp
from bs4 import BeautifulSoup
import pandas as pd
import logging

from models import certified_taxi_drivers


logger = logging.getLogger(__name__)

REGIONS_LIST: list[str] = ['moskva']
URL = 'https://pro.yandex.ru/ru-ru/{region}/knowledge-base/taxi/common/parks'

async def certificate_taxi(add_in_the_file):
    logger.info('[+] Start certified taxi drivers parsing...')

    for region in REGIONS_LIST:
        await session_status_and_code(region)

"""Accessing the page until the html code of the page is received."""
async def session_status_and_code(region):
    async with aiohttp.ClientSession() as session:
        async with session.get(URL.format(region=region)) as resp:
            if int(resp.status) != 500:
                html_code: str = await resp.text()
                await add_in_the_file(html_code, region)
            else:
                await session_status_and_code(region)

"""Work on html analysis and writing to a .csv file."""
async def add_in_the_file(html_code, region):
    soup = BeautifulSoup(html_code,'lxml')

    csv_res_path = environ['RESULTS_CERT_YA_TAXIS'] + f'{region}.csv'
    open(csv_res_path, 'a').close()
    certificate_taxi_list = []

    for req in soup.select("div.accordion_accordion__7KkXQ"):
        company: str = str(req.select_one("p.body2").string)
        phone: str = str(req.select("p.body2.icon-list-item_text__jP3Nc")[1].string)
        addres: str = str(req.select("p.body2.icon-list-item_text__jP3Nc")[2].string)

        cert_drivers = certified_taxi_drivers(company, phone, addres)
        certificate_taxi_list.append(cert_drivers.to_list())
    
    df = pd.DataFrame(certificate_taxi_list, columns=['name', 'phone', 'addres'])
    df.to_csv(path_or_buf=csv_res_path)

    logger.info('[+] All information about certified taxis has been obtained...')
