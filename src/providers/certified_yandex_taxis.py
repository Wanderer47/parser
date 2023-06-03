from os import environ
from typing import Optional
from dataclasses import asdict
import time
from random import uniform

from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
import pandas as pd
import logging

from models import Certified_taxi_drivers
from tasks import Analyzer


logger = logging.getLogger(__name__)

REGIONS_FILE_NAME = 'certified_regions_list.txt'
URL = 'https://pro.yandex.ru/ru-ru/{region}/knowledge-base/taxi/common/parks'
with open('{regions_path}{regions_file_name}'.format(
                                        regions_path=environ['REGIONS'],
                                        regions_file_name=REGIONS_FILE_NAME
                                                        ), 'r') as regions:
    REGIONS_LIST = regions.read().split('\n')


async def get_sert_partners(add_in_the_file) -> None:
    logger.info('[+] Start certified taxi drivers parsing...')

    csv_res_path = environ['RESULTS_CERT_YA_TAXIS'] + 'all_partners.csv'
    all_df = pd.DataFrame(columns=['region', 'name', 'phone', 'address'])

    """ Initialization chrome webdriver. """
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("enable-automation")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-extensions")
    options.add_argument("--dns-prefetch-disable")
    options.add_argument("--disable-gpu")

    try:
        driver = webdriver.Chrome(options=options)
    except Exception as ex:
        logger.info('===> driver exception')
        logger.warning(ex)

    for region in REGIONS_LIST:
        time.sleep(uniform(3.0, 15.0))
        df = await add_in_the_file(region, driver)
        if df is not None:
            all_df = pd.concat([all_df, df], ignore_index=True)

    driver.quit()

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


async def add_in_the_file(region, driver) -> pd.DataFrame:
    certificate_taxi_list = []

    """ Navigating to a page. """
    try:
        driver.get(URL.format(region=region))
    except Exception as ex:
        logger.info('===> website exception')
        logger.warning(ex)

    """
    Select drop-down block with info about partner ->
    div.accordion_accordion__7KkXQ
    """
    partners: list[WebElement] = driver.find_elements(
                                    By.CLASS_NAME,
                                    'accordion_accordion__7KkXQ'
                                    )
    for partner in partners:
        company: Optional[str] = None
        phone: Optional[str] = None
        addres: Optional[str] = None

        title_elem: WebElement = partner.find_element(
                                    By.CLASS_NAME,
                                    'accordion_titleWrapper__2ogdZ'
                                    )
        company = title_elem.find_element(By.TAG_NAME, 'span').text

        """
        If drop-down list roll up then we click and open it
        """
        text_drop_down = partner.find_element(
                                            By.CLASS_NAME,
                                            'accordion_textWrapper__2l6lu'
                                            )
        get_drop_down_style = text_drop_down.get_attribute("style")
        if get_drop_down_style != 'height: auto;':
            title_elem.click()
            time.sleep(uniform(2.0, 10.0))

        """
        Geting the text from dorp-down list
        """
        text_elem: list[WebElement] = partner.find_elements(
                                        By.CLASS_NAME,
                                        'body2.icon-list-item_text__jP3Nc'
                                        )
        phone = text_elem[1].find_element(By.TAG_NAME, 'span').text
        addres = text_elem[2].find_element(By.TAG_NAME, 'span').text

        cert_drivers = Certified_taxi_drivers(region, company, phone, addres)
        certificate_taxi_list.append(asdict(cert_drivers))

    df = pd.DataFrame(certificate_taxi_list,
                      columns=['region', 'name', 'phone', 'address'])

    logger.info(f'[+] Finish {region} certified taxi drivers parsing...')

    return df


async def certificate_taxi() -> None:
    await get_sert_partners(add_in_the_file)
