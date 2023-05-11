import time
from typing import Optional, Generator, AsyncGenerator
import logging
from os import environ
from dataclasses import asdict

import aiohttp
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
import pandas as pd

from models import City_partners_organizatons
from tasks import Analyzer


logger = logging.getLogger(__name__)

REGIONS_LIST = ['moscow']
URL_REGION = "https://taxi.yandex.ru/{region}/parks"
URL_PARK = "https://taxi.yandex.ru/{region}/parks/{park}"


async def get_park_id_and_name(region) -> \
                                        AsyncGenerator[tuple[str, str], None]:
    logger.info('[+] Start city partners parsing...')

    """ Initialization chrome webdriver. """
    options = webdriver.ChromeOptions()
    options.headless = True
    options.add_argument("window-size=1920x1080")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=options)

    """ Navigating to a page. """
    driver.get(URL_REGION.format(region=region))
    time.sleep(2)

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
            yield (park.get_attribute('href').split("/")[-1], park.text)

        """
        We are waiting for the data to be sorted and parsed.
        After that we scroll the scroll bar of the site.
        """
        time.sleep(1)
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

        analyzer = Analyzer(csv_res_path, df_no_duplicates, logger)
        analyzer.get_differents()

        open(csv_res_path, 'w').close()  # Clearing .csv file
        df_no_duplicates.to_csv(path_or_buf=csv_res_path, index=False)
    else:
        logger.info('[+] Empty DataFrame')


async def start_parsing() -> None:
    for region in REGIONS_LIST:
        park_id_and_name = get_park_id_and_name(region)
        data = get_data_from_park_id(park_id_and_name, region)
        await wright_to_file(data, region)
