import time
from typing import Optional, Generator
import logging
from os import environ

import aiohttp
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
import pandas as pd

from models import city_partners_organizatons


logger = logging.getLogger(__name__)
logging.basicConfig(
        filename='{log_path}ya_taxi_partners.log'.format(
            log_path=environ['PARSER_LOGS']),
        filemode='w',
        level=logging.DEBUG
        )

REGIONS_LIST: list[str] = ['moscow']
URL_REGION = "https://taxi.yandex.ru/{region}/parks"
URL_PARK = "https://taxi.yandex.ru/{region}/parks/{park}"


async def get_park_id_and_name_gen(region):
    logger.info('[+] Start city partners parsing...')

    options = webdriver.ChromeOptions()
    options.headless = True
    options.add_argument("window-size=1920x1080")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=options)

    driver.get(URL_REGION.format(region=region))
    time.sleep(2)

    scroll_bar_element = driver.find_element(by=By.CLASS_NAME,
                                             value="ParkList__list")

    pre_height = 0
    new_height = 0

    while True:
        park_links: Generator[WebElement, None, None]
        park_links = (park for park in driver.find_elements(
            by=By.CLASS_NAME, value="Park__link"
            ))

        for park in park_links:
            yield (park.get_attribute('href').split("/")[-1], park.text)

        """
        We are waiting for the data to be sorted and parsed.
        After that we scroll the scroll bar of the site
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
            logger.debug('[+] Found all partners id...')
            break

    driver.close()


async def get_data_from_park_id(park_id_gen, region):
    async for park in park_id_gen:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    URL_PARK.format(region=region, park=park[0])) as resp:
                html_code: str = await resp.text()

        soup = BeautifulSoup(html_code, 'lxml')

        organization_id: Optional[str] = None
        organization_name: Optional[str] = None
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

        data = city_partners_organizatons(
                organization_id,
                organization_name,
                organization_full_name,
                ogrn,
                inn
                )
        yield data.to_list()
        logger.debug('[+] add to list')


async def wright_to_file(data_to_list_gen, region):
    csv_res_path = environ['RESULTS_YA_TAXI_PARTNERS'] + f'{region}.csv'
    """ If there is no .csv file, then we create it """
    open(csv_res_path, 'a').close()
    logger.info('created .csv file')

    open(csv_res_path, 'w').close()  # Clearing .csv file

    df = pd.DataFrame(columns=[
                              'PARK_ID',
                              'NAME',
                              'FULL NAME',
                              'OGRN',
                              'INN'
                              ])

    async for data in data_to_list_gen:
        df_new = pd.DataFrame([data],
                              columns=[
                                  'PARK_ID',
                                  'NAME',
                                  'FULL NAME',
                                  'OGRN',
                                  'INN'
                                  ])
        df = pd.concat([df, df_new], ignore_index=True)

    df.drop_duplicates()
    logger.debug(f'add data on pandas data frame {df}')
    df.to_csv(path_or_buf=csv_res_path)


async def start_parsing():
    for region in REGIONS_LIST:
        await wright_to_file(
                get_data_from_park_id(
                    get_park_id_and_name_gen(region),
                    region
                    ),
                region
                )
