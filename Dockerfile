FROM python:3.10

WORKDIR /app
ENV PYTHONPATH=/app/src
RUN mkdir -p src/

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY src/ src/

ENV RESULTS_CERT_YA_TAXIS /app/results/certificate_taxi/
ENV RESULTS_YA_TAXI_PARTNERS /app/results/city_partners/

RUN mkdir -p $RESULTS_CERT_YA_TAXIS
RUN mkdir -p $RESULTS_YA_TAXI_PARTNERS

ENV PARSER_LOGS /app/logs/
ARG WRITE_LOGS_TO_FILE
ENV WRITE_LOGS_TO_FILE $WRITE_LOGS_TO_FILE
RUN mkdir -p $PARSER_LOGS

# contains files with a list of regions
ENV REGIONS /app/regions/
RUN mkdir -p $REGIONS

# install google chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get -y update
RUN apt-get install -y google-chrome-stable

# install chromedriver
RUN apt-get install -yqq unzip
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

ENTRYPOINT ["python3.10", "src/app.py"]
