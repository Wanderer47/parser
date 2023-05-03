from os import environ
from typing import Optional

import aiohttp
from bs4 import BeautifulSoup
import pandas as pd
import logging

from models import Certified_taxi_drivers
from tasks import Analyzer


logger = logging.getLogger(__name__)

REGIONS_LIST = ['moskva']
URL = 'https://pro.yandex.ru/ru-ru/{region}/knowledge-base/taxi/common/parks'


async def certificate_taxi(add_in_the_file) -> None:
    logger.info('[+] Start certified taxi drivers parsing...')

    csv_res_path = environ['RESULTS_CERT_YA_TAXIS'] + 'all_partners.csv'
    all_df = pd.DataFrame(columns=['REGION', 'NAME', 'PHONE', 'ADDRESS'])

    for region in REGIONS_LIST:
        df = await session_status_and_code(region)
        if df is not None:
            all_df = pd.concat([all_df, df], ignore_index=True)

            all_df_no_duplicates = all_df.drop_duplicates(
                                                keep="first",
                                                ignore_index=True
                                                )

            if all_df_no_duplicates is not None:
                open(csv_res_path, 'a').close()

                analyzer = Analyzer(csv_res_path, all_df_no_duplicates, logger)
                analyzer.get_differents()

                open(csv_res_path, 'w').close()

                all_df_no_duplicates.to_csv(
                                            path_or_buf=csv_res_path,
                                            index=False
                                            )


async def session_status_and_code(region) -> pd.DataFrame | None:
    """Accessing the page until the html code of the page is received."""
    async with aiohttp.ClientSession() as session:
        async with session.get(URL.format(region=region)) as resp:
            if int(resp.status) == 404:
                return
            if int(resp.status) != 500:
                content: str = await resp.text()
                return await add_in_the_file(content, region)
            else:
                await session_status_and_code(region)


async def add_in_the_file(content, region) -> pd.DataFrame:
    """Work on html analysis and writing to a .csv file."""
    soup = BeautifulSoup(content, 'lxml')

    certificate_taxi_list = []

    for req in soup.select("div.accordion_accordion__7KkXQ"):
        company: Optional[str] = None
        phone: Optional[str] = None
        addres: Optional[str] = None

        company = str(req.select_one("p.body2").string)
        phone = str(
                req.select("p.body2.icon-list-item_text__jP3Nc")[1].string)
        addres = str(
                req.select("p.body2.icon-list-item_text__jP3Nc")[2].string)

        cert_drivers = Certified_taxi_drivers(region, company, phone, addres)
        certificate_taxi_list.append(cert_drivers.to_dict())

    df = pd.DataFrame(certificate_taxi_list,
                      columns=['REGION', 'NAME', 'PHONE', 'ADDRESS'])

    """
    If you want to withdraw partners for each city separately, then uncomment.
    """
    """
    csv_res_path = environ['RESULTS_CERT_YA_TAXIS'] + f'{region}.csv'
    open(csv_res_path, 'a').close()

    analyzer = Analyzer(csv_res_path, df, logger)
    analyzer.get_differents()

    open(csv_res_path, 'w').close()

    df.to_csv(path_or_buf=csv_res_path, index=False)
    """

    logger.info('[+] Finish certified taxi drivers parsing...')

    return df
