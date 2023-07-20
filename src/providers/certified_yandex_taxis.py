from os import environ
from typing import Optional
from dataclasses import asdict
from random import uniform
import asyncio
import time

from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
import pandas as pd
import logging
import aiohttp

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


async def get_sert_partners(get_data_frame_from_region) -> None:
    """ Runs the Analyzer and writes the data to a file.

    Args:
        get_data_frame_from_region: The get_sert_partners is decorator function
            receiving an input function get_data_frame_from_region, that
            returns a DataFrame with data about the partners of this region.
    """
    logger.info('[+] Start certified taxi drivers parsing...')

    csv_res_path = environ['RESULTS_CERT_YA_TAXIS'] + 'all_partners.csv'
    all_df = pd.DataFrame(columns=['region', 'name', 'phone', 'address'])

    # Initialization chrome webdriver.
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
        logger.warning(f'!!! {ex}')

    for region in REGIONS_LIST:
        async with aiohttp.ClientSession() as session:
            async with session.get(URL.format(region=region)) as resp:
                if int(resp.status) == 404:
                    logger.info(f'status 404: {region}')
                elif len(resp.history) != 0 and \
                        int(resp.history[0].status) == 302:
                    logger.info(f'status 302: {region}')
                else:
                    # A delay that mimics the user's behavior when switching to
                    # another site.
                    await asyncio.sleep(uniform(1.0, 10.0))
                    # Get DataFrame with information about the partners of
                    # this region.
                    df = await get_data_frame_from_region(region, driver)
                    if df is not None:
                        # Combine the received DF with the DF from
                        # the previous ones regions.
                        all_df = pd.concat([all_df, df], ignore_index=True)

    driver.quit()

    all_df_no_duplicates = all_df.drop_duplicates(
                                        keep="first",
                                        ignore_index=True
                                        )

    if all_df_no_duplicates is not None:
        # Create a file if it has not been created before.
        open(csv_res_path, 'a').close()

        analyzer_phone = Analyzer(
                            old_file_path=csv_res_path,
                            df=all_df_no_duplicates,
                            column='phone',
                            logger=logger
                            )
        analyzer_phone.get_differents()

        # Delete old file contents.
        open(csv_res_path, 'w').close()

        # Write new data to a .csv file.
        all_df_no_duplicates.to_csv(
                                    path_or_buf=csv_res_path,
                                    index=False
                                    )


async def get_data_frame_from_region(region, driver) -> pd.DataFrame:
    """ Parse data from websait.

    Args:
        region: The city whose data we are parsing.
        driver:

    Returns:
        Returns a DataFrame containing all the data of this city.

        City data:
            region: The city whose data we are parsing.
            name: Name of the partner.
            phone: Partner's phone number.
            address: Partner's address.
    """
    certificate_taxi_list = []

    try:
        # Navigating to a page.
        t_s = time.time()
        driver.get(URL.format(region=region))
        t_e = time.time()
        d = t_e - t_s
        logger.warning(f'driver.get ===> {d}')
    except Exception as ex:
        logger.warning(f'!!! {ex}')

    # We get a list WebElement containing info about partner ->
    # <div class="accordion_accordion__7KkXQ">
    t_s = time.time()
    partners: list[WebElement] = driver.find_elements(
                                    By.CLASS_NAME,
                                    'accordion_accordion__7KkXQ'
                                    )
    t_e = time.time()
    d = t_e - t_s
    logger.warning('partners: driver.find_elements ' +
                f'(accordion_accordion__7KkXQ) ===> {d}')

    for partner in partners:
        company: Optional[str] = None
        phone: Optional[str] = None
        addres: Optional[str] = None

        # We get WebElement containing partner name ->
        # <div class="accordion_titleWrapper__2ogdZ">
        #   ...
        #       <span>partner_name</span>
        t_s = time.time()
        title_elem: WebElement = partner.find_element(
                                    By.CLASS_NAME,
                                    'accordion_titleWrapper__2ogdZ'
                                    )
        t_e = time.time()
        d = t_e - t_s
        logger.warning(f'title_elem: driver.find_elements \
                (accordion_titleWrapper__2ogdZ) ===> {d}')

        t_s = time.time()
        company = title_elem.find_element(By.TAG_NAME, 'span').text
        t_e = time.time()
        d = t_e - t_s
        logger.warning(f'company: driver.find_elements (span) ===> {d}')

        # If drop-down list roll up then we click and open it ->
        # <div class="accordion_textWrapper__2l6lu" style="height: 0px;">
        #
        # "height: 0px;" - roll up drop-down
        # "height: auto;" - roll down drop-down
        t_s = time.time()
        text_drop_down = partner.find_element(
                                            By.CLASS_NAME,
                                            'accordion_textWrapper__2l6lu'
                                            )
        t_e = time.time()
        d = t_e - t_s
        logger.warning('text_drop_down: driver.find_elements ' +
                    f'(accordion_textWrapper__2l6lu) ===> {d}')

        t_s = time.time()
        get_drop_down_style = text_drop_down.get_attribute("style")
        t_e = time.time()
        d = t_e - t_s
        logger.warning('get_drop_down_style: text_drop_down.get_attribute ' +
                    f'(style) ===> {d}')
        if get_drop_down_style != 'height: auto;':
            title_elem.click()
            # Delay in loading clicks on the site field.
            await asyncio.sleep(2)

        # Geting list WebElement containing the necessary data from
        # the partner ->
        # <div class="accordion_textWrapper__2l6lu" style="height: auto;">
        #   ...
        #       <p class="body2 icon-list-item_text__jP3Nc">
        #           <span>necessary_data</span>
        t_s = time.time()
        text_elem: list[WebElement] = partner.find_elements(
                                        By.CLASS_NAME,
                                        'body2.icon-list-item_text__jP3Nc'
                                        )
        t_e = time.time()
        d = t_e - t_s
        logger.warning('text_elem: partner.find_elements ' +
                    f'(body2.icon-list-item_text__jP3Nc) ===> {d}')

        t_s = time.time()
        phone = text_elem[1].find_element(By.TAG_NAME, 'span').text
        t_e = time.time()
        d = t_e - t_s
        logger.warning('phone: text_elem[1].find_element ' +
                    f'(span) ===> {d}')

        t_s = time.time()
        addres = text_elem[2].find_element(By.TAG_NAME, 'span').text
        t_e = time.time()
        d = t_e - t_s
        logger.warning('addres: text_elem[2].find_element ' +
                    f'(span) ===> {d}')

        # Wrap the data in a model, then add it to the certificate_taxi_list
        # in the form of a dictionary.
        cert_drivers = Certified_taxi_drivers(region, company, phone, addres)
        certificate_taxi_list.append(asdict(cert_drivers))

    # Converting a list with data to DataFrame.
    df = pd.DataFrame(certificate_taxi_list,
                      columns=['region', 'name', 'phone', 'address'])

    logger.info(f'[+] Finish {region} certified taxi drivers parsing...')

    return df


async def start_certificate_taxi_scraping() -> None:
    await get_sert_partners(get_data_frame_from_region)
