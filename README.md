Build docker-compose
------------------------
``` docker-compose build ```

Up container
------------------------
``` docker-compose up ```

If you want to run the container in detach mode, use "-d" key:
``` docker-compose up -d ```

Building and up the container at the same time
-----------------------------------------------
``` docker-compose up --build ```

Volumes
------------
``` ./results/certificate_taxi:/app/results/certificate_taxi ``` 
<--- the directory containing the files with the results of the script 
certified_yandex_taxis.py, receiveng data from the 
<https://pro.yandex.ru/ru-ru/tomsk/knowledge-base/taxi/common/parks> site

``` ./results/city_partners:/app/results/city_partners ``` 
<--- the directory containing the files with the results of the script 
yandex_taxi_partners.py, receiveng data from the 
<https://taxi.yandex.ru/moscow/parks/> site

``` ./logs:/app/logs ``` 
<--- directory containing log files

``` ./regions:/app/regions ``` 
<--- directory containing files with cities for parsing

Args
------------
``` WRITE_LOGS_TO_FILE ``` <--- If you want to write a log to a file 
select True otherwise False

Environments
-------------
``` RESULTS_CERT_YA_TAXIS ``` 
<--- the directory containing the files with the results of the script 
certified_yandex_taxis.py

``` RESULTS_YA_TAXI_PARTNERS ``` 
<--- the directory containing the files with the results of the script 
yandex_taxi_partners.py

``` WRITE_LOGS_TO_FILE ``` 
<--- if you want to write a log to a file select True otherwise False 
set in Args.


``` PARSER_LOGS ``` 
<--- the path to the folder containing file with log

``` REGIONS ``` 
<--- the path to the folder containing files with cities
