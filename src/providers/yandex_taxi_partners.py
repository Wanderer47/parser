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
    logger.info('[+] Start city partners parsing...')

    page_number = 0
    while True:
        time.sleep(uniform(1.0, 5.0))
        response = requests.request("POST",
                                    API_URL.format(page_number=page_number),
                                    headers=API_HEADERS,
                                    data=API_PAYLOAD
                                    )

        data = json.loads(response.text)

        if len(data["parks"]) == 0:
            break
        else:
            page_number += 1

        park_links = (park for park in data["parks"])
        for park in park_links:
            yield (park["parkid"], park["name"])


async def get_park_id_and_name_selenium(region) -> \
                                        AsyncGenerator[tuple[str, str], None]:
    logger.info('[+] Start city partners parsing...')

    """ Initialization chrome webdriver. """
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("enable-automation")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-extensions")
    options.add_argument("--dns-prefetch-disable")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)

    """ Navigating to a page. """
    driver.get(URL_REGION.format(region=region))
    time.sleep(uniform(2.0, 3.0))

    scroll_bar_element = driver.find_element(by=By.CLASS_NAME,
                                             value="ParkList__list")

    pre_height = 0
    new_height = 0

    while True:
        """ Getting park links from a submerged scrollbar. """
        park_links: Generator[WebElement, None, None] = \
            (park for park in driver.find_elements(
                                                by=By.CLASS_NAME,
                                                value="Park__link"
                                                   )
             )

        for park in park_links:
            try:
                yield (park.get_attribute('href').split("/")[-1], park.text)
            except StaleElementReferenceException as state_ex:
                logger.exception(f'[-] Selenium exception {str(state_ex)}')
                break

        """
        We are waiting for the data to be sorted and parsed.
        After that we scroll the scroll bar of the site.
        """
        time.sleep(uniform(1.0, 2.0))
        driver.execute_script(
                "arguments[0].scrollTop = arguments[0].scrollHeight",
                scroll_bar_element)
        new_height = driver.execute_script(
                "return arguments[0].scrollHeight", scroll_bar_element)
        if pre_height < new_height:
            pre_height = driver.execute_script(
                    "return arguments[0].scrollHeight",
                    scroll_bar_element)
        else:
            logger.info('[+] Finish city partners parsing...')
            break

    driver.close()


async def get_data_from_park_id(park_id, region) -> \
                                        AsyncGenerator[dict[str, str], None]:
    async for park in park_id:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    URL_PARK.format(region=region, park=park[0])) as resp:
                content: str = await resp.text()

        soup = BeautifulSoup(content, 'lxml')

        organization_full_name: Optional[str] = None
        inn: Optional[str] = None
        ogrn: Optional[str] = None

        organization_id = park[0]
        organization_name = park[1]

        for req in soup.select('div.HeaderInfo__details'):
            organization_full_name = req.select('span')[0].text

            for info_tag in req.select('span'):
                if (info_tag.text.split(maxsplit=1)[0] == 'ОГРН:'):
                    ogrn = info_tag.text.split(maxsplit=1)[1]
                elif (info_tag.text.split(maxsplit=1)[0] == 'ИНН:'):
                    inn = info_tag.text.split(maxsplit=1)[1]

        data = City_partners_organizatons(
                organization_id,
                organization_name,
                organization_full_name,
                ogrn,
                inn
                )
        yield asdict(data)
        logger.info('[+] Transform data to dict')


async def wright_to_file(data_to_dict, region) -> None:
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

        df = pd.concat([df, data_normalize], ignore_index=True)

        df_no_duplicates = df.drop_duplicates(
                                            subset='park_id',
                                            keep="first",
                                            ignore_index=True
                                            )

    if df_no_duplicates is not None:
        # If there is no .csv file, then we create it
        open(csv_res_path, 'a').close()
        logger.info('[+] Created .csv file')

        analyzer = Analyzer(csv_res_path, df_no_duplicates, 'park_id', logger)
        analyzer.get_differents()

        open(csv_res_path, 'w').close()  # Clearing .csv file
        df_no_duplicates.to_csv(path_or_buf=csv_res_path, index=False)
    else:
        logger.info('[+] Empty DataFrame')


async def start_ya_partners_scraping() -> None:
    '''
    If you want to get an park_id_and_name using the api then set <True>
    else set <False>
    '''
    park_id_and_name_api = True

    for region in REGIONS_LIST:
        if park_id_and_name_api:
            park_id_and_name = get_park_id_and_name_api(region)
        else:
            park_id_and_name = get_park_id_and_name_selenium(region)
        data = get_data_from_park_id(park_id_and_name, region)
        await wright_to_file(data, region)
