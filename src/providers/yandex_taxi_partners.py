import time
from random import uniform
from typing import Optional, Generator, AsyncGenerator
import logging
from os import environ
from dataclasses import asdict
import json

import aiohttp
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
import pandas as pd

from models import City_partners_organizatons
from tasks import Analyzer


logger = logging.getLogger(__name__)

REGIONS_LIST = ['moscow']
URL_REGION = "https://taxi.yandex.ru/{region}/parks"
URL_PARK = "https://taxi.yandex.ru/{region}/parks/{park}"

API_PAYLOAD = "{\"zone_name\": \"moscow\", \"search_query\": null}"
API_URL = "https://taxi.yandex.ru/3.0/pricecat?page={page_number}"
API_HEADERS = {
  'Accept': 'application/json',
  'Accept-Encoding': 'gzip, deflate, br',
  'Accept-Language': 'ru',
  'Cache-Control': 'no-cache,no-store,must-revalidate,max-age=-1,private',
  'Connection': 'keep-alive',
  'Content-Length': '42',
  'Content-Type': 'application/json',
  'Cookie': 'yandexuid=4827174231668976889; yuidss=4827174231668976889; ymex=1984336889.yrts.1668976889#1984336889.yrtsi.1668976889; skid=8037721971668976892; is_gdpr=0; _ym_uid=1668976893938507875; _ym_d=1668976899; gdpr=0; yashr=3509454561674041044; is_gdpr_b=CKWxOxDppgEoAg==; i=HRr+tAiv2YmvQtBTctKi4+LXH6gLXqQJv1ieKrsYJCkyNZPaDBZQdEXAggod7GiG8S96gRet3mWYVWsLmhS8N1ZBuho=; _LOCALE_=ru_ru; font_loaded=YSv1; ys=wprid.1684096089369808-9517953582395188968-balancer-l7leveler-kubr-yp-sas-5-BAL-5924; yp=1999456090.pcs.0#1684700890.mcv.0#1684700890.mcl.#1684700890.szm.1%3A1920x1080%3A1888x926#1686774491.hdrc.0; cycada=BWEWGGfY6gDQkRsLfDJGoeMqRn8vKTfpx5HS8/0aMGA=; _ym_isad=2; _ym_visorc=b; country=RU; _yasc=XCjtULFEJQGOw40HJgKUR9ZnfIyoMChYOyp8WIbaXkFvsuB3UqJhT7yJktnsm2Yswb2RYI6aEg==; bh=EigiQ2hyb21pdW0iO3Y9IjExMyIsICJOb3QtQS5CcmFuZCI7dj0iMjQiGgUieDg2IiIQIjExMy4wLjU2NzIuMTI2IioCPzA6ByJMaW51eCJCByI1LjQuMCJKBCI2NCJSOSJDaHJvbWl1bSI7dj0iMTEzLjAuNTY3Mi4xMjYiLCJOb3QtQS5CcmFuZCI7dj0iMjQuMC4wLjAiIg==; _yasc=qw4PsI34qkLNkKOXnmPRBDuxYYyCiywLDvFiS8Tz4oduaIhaXb2a3i+FtyiMpyK5stIQNI6zsw==; i=g4KoXhROPIRoJW9kf663d7eN5xOVOcKoBOvSlqHTxHd7/hFqTwBC8u6+HHuISbFey3f9I0li02gLSincIUO2PHrjIzA=; yandexuid=9373000231684660717',
  'Expires': '-1',
  'Host': 'taxi.yandex.ru',
  'Origin': 'https://taxi.yandex.ru',
  'Referer': 'https://taxi.yandex.ru/moscow/parks/',
  'sec-ch-ua': '"Chromium";v="113", "Not-A.Brand";v="24"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Linux"',
  'Sec-Fetch-Dest': 'empty',
  'Sec-Fetch-Mode': 'cors',
  'Sec-Fetch-Site': 'same-origin',
  'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
  'x-requested-uri': 'https://taxi.yandex.ru/moscow/parks/',
  'X-Requested-With': 'XMLHttpRequest'
}


async def get_park_id_and_name_api(region) -> \
                                        AsyncGenerator[tuple[str, str], None]:
    """ Get a list of partners and their ID.

    Parses the list of partners and their IDs using the API.

    Args:
        region: The city whose data is parsed.

    Returns:
        Asynchronous generator containing a tuple of the ID of the park
        and the name of the partner.

        Tuple:
            park["parkid"]: ID of the park.
            park["name"]: The name of the partner.
    """
    logger.info('[+] Start city partners parsing...')

    # Page counter, default value -> 0
    page_number = 0
    while True:
        time.sleep(uniform(1.0, 5.0))
        response = requests.request("POST",
                                    API_URL.format(page_number=page_number),
                                    headers=API_HEADERS,
                                    data=API_PAYLOAD
                                    )

        # The API returns json. Deserialize it to a Python object.
        data = json.loads(response.text)

        # If object is empty, exit form loop.
        if len(data["parks"]) == 0:
            break
        else:
            page_number += 1

        # Get data from json.
        park_links = (park for park in data["parks"])
        for park in park_links:
            yield (park["parkid"], park["name"])


async def get_data_from_park_id(park_id_and_name, region) -> \
                                        AsyncGenerator[dict[str, str], None]:
    """ Get data about partner.

    Args:
        park_id_and_name: Asynchronous generator containing a tuple of the
            ID of the park and the name of the partner.
        region: The city whose data is parsed.

    Returns:
        Asynchronous generator containing dict vith data.

        Data:
            organization_id: ID of the park.
            organization_name: The name of the partner.
            organization_full_name: The full name of the partner.
            ogrn: Main state registration number.
            inn: Taxpayer identification number.
    """

    async for park in park_id_and_name:
        async with aiohttp.ClientSession() as session:
            # If an exception occurs, we try to establish a connection.
            # The timer is the time after which we try to reconnect.
            timer = 0
            while True:
                try:
                    async with session.get(
                            URL_PARK.format(region=region, park=park[0])
                                          ) as resp:
                        content: str = await resp.text()
                    break
                except Exception as ex:
                    logger.warn(ex)
                    pass

                if timer == 300:
                    break
                else:
                    timer += 60
                    time.sleep(timer)

        # Use bs4 to parsing received HTML document.
        soup = BeautifulSoup(content, 'lxml')

        organization_full_name: Optional[str] = None
        inn: Optional[str] = None
        ogrn: Optional[str] = None

        organization_id = park[0]
        organization_name = park[1]

        # Search for data in html ->
        # <div class="HeaderInfo__details">
        for req in soup.select('div.HeaderInfo__details'):
            if len(req.select('span')) != 0:
                organization_full_name = req.select('span')[0].text

                # Search by the first word.
                for info_tag in req.select('span'):
                    if (info_tag.text.split(maxsplit=1)[0] == 'ОГРН:'):
                        ogrn = info_tag.text.split(maxsplit=1)[1]
                    elif (info_tag.text.split(maxsplit=1)[0] == 'ИНН:'):
                        inn = info_tag.text.split(maxsplit=1)[1]
            else:
                logger.info('!!! Get empty data list from page.')

        # Wrap the data in a model and converting to dict.
        data = City_partners_organizatons(
                organization_id,
                organization_name,
                organization_full_name,
                ogrn,
                inn
                )
        yield asdict(data)


async def wright_to_file(data_to_dict, region) -> None:
    """ Wrigth data to file.

    Args:
        data_to_dict: Asynchronous generator containing dict vith data.
        region: The city whose data is parsed.
    """

    csv_res_path = environ['RESULTS_YA_TAXI_PARTNERS'] + f'{region}.csv'

    df = pd.DataFrame(columns=[
                              'park_id',
                              'name',
                              'full_name',
                              'ogrn',
                              'inn'
                              ]
                      )

    df_no_duplicates: pd.DataFrame | None = None
    async for data in data_to_dict:
        data_normalize = pd.json_normalize(data)

        # Combining data.
        df = pd.concat([df, data_normalize], ignore_index=True)

        df_no_duplicates = df.drop_duplicates(
                                            subset='park_id',
                                            keep="first",
                                            ignore_index=True
                                            )

    if df_no_duplicates is not None:
        # Create a file if it has not been created before.
        open(csv_res_path, 'a').close()
        logger.info('[+] Created .csv file')

        analyzer = Analyzer(
                            old_file_path=csv_res_path,
                            df=df_no_duplicates,
                            column='park_id',
                            logger=logger
                            )
        analyzer.get_differents()

        # Delete old file contents.
        open(csv_res_path, 'w').close()

        # Write new data to a .csv file.
        df_no_duplicates.to_csv(path_or_buf=csv_res_path, index=False)
    else:
        logger.info('[+] Empty DataFrame')


async def start_ya_partners_scraping() -> None:
    for region in REGIONS_LIST:
        park_id_and_name = get_park_id_and_name_api(region)
        data = get_data_from_park_id(park_id_and_name, region)
        await wright_to_file(data, region)
