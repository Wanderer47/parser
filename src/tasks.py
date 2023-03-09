import time
import logging

import aiohttp
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd

#from app import application
#from repository import CertificateTaxiRepository
from models import  certified_taxi_drivers


logger = logging.getLogger(__name__)

async def certificate_taxi():
    logger.info('[+] Start certified taxi drivers parsing...')

    regions: list[str] = ['moskva']
    
    for region in regions:

        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://pro.yandex.ru/ru-ru/{region}/knowledge-base/taxi/common/parks') as resp:
                html_code: str = await resp.text()

        soup = BeautifulSoup(html_code,'lxml')

        csv_res_path = f'/app/results/certificate_taxi/{region}.csv'
        open(csv_res_path, 'a').close()
        certificate_taxi_list = []

        for req in soup.select("div.accordion_accordion__7KkXQ"):
            company: str = str(req.select_one("p.body2").string)
            phone: str = str(req.select("p.body2.icon-list-item_text__jP3Nc")[1].string)
            addres: str = str(req.select("p.body2.icon-list-item_text__jP3Nc")[2].string)

            cert_drivers = certified_taxi_drivers(company, phone, addres)
            certificate_taxi_list.append(cert_drivers.to_dict())
        
        with open(csv_res_path, 'w') as file:
            df = pd.DataFrame(certificate_taxi_list, columns=['name', 'phone', 'addres'])
            df.to_csv(path_or_buf=file)

    logger.info('[+] All information about certified taxis has been obtained...')

async def city_partners():
    logger.info('[+] Start city partners parsing...')

    parks_list: list[str] = ['1956789345', '400000047422']

    options = webdriver.ChromeOptions()
    options.headless = True
    options.add_argument("window-size=1920x1080")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=options)
    
    driver.get("https://taxi.yandex.ru/moscow/parks")
    time.sleep(2)
    

    scroll_bar_element = driver.find_element(by=By.CLASS_NAME, value="ParkList__list")

    pre_height = 0
    new_height = 0

    #while True:
    #    park_links = driver.find_elements(by=By.CLASS_NAME, value="Park__link")

    #    for park in park_links:
    #        parks_list.append(park.get_attribute('href').split("/")[-1])
    #    
    #    time.sleep(1)
    #    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scroll_bar_element)
    #    new_height = driver.execute_script("return arguments[0].scrollHeight", scroll_bar_element)
    #    if pre_height < new_height:
    #        pre_height = driver.execute_script("return arguments[0].scrollHeight", scroll_bar_element)
    #    else:
    #        logger.debug('[+] Found all partners id...')
    #        break
        
    for park in parks_list:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://taxi.yandex.ru/' + 'moscow' + '/parks/' + park) as resp:
                html_code: str = await resp.text()

        soup = BeautifulSoup(html_code,'lxml')

        for req in soup.select('div.HeaderInfo__details'):
            organization: str
            inn: str
            ogrn: str

            for info_tag in req.select('span'):
                #print(info_tag.text.split(maxsplit=1))
                if(info_tag.text.split(maxsplit=1)[0] == 'ОГРН:'):
                    ogrn: str = info_tag.text.split(maxsplit=1)[1]
                elif(info_tag.text.split(maxsplit=1)[0] == 'ИНН:'):
                    inn: str = info_tag.text.split(maxsplit=1)[1]
                else:
                    organization: str = info_tag.text
                
            data = (organization, ogrn, inn)
            print(data)

