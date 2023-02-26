FROM python:3.10-buster

WORKDIR /app
ENV PYTHONPATH=/app/src
RUN mkdir -p src/

COPY requirements.txt requirements.txt
#RUN pip install --default-timeout=1000 --no-cache-dir --upgrade pip \
#    && pip install --no-cache-dir -r requirements.txt

RUN pip install -r requirements.txt

COPY src/ src/

RUN mkdir -p migrations/
COPY alembic.ini .
#COPY migrations/ migrations/

