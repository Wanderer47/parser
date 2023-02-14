FROM python:3.10

WORKDIR /app
ENV PYTHONPATH=/app/src
RUN mkdir -p src/

COPY requirements.txt requirements.txt
RUN pip install --default-timeout=1000 --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY src/ src/

RUN mkdir -p migrations/
COPY alembic.ini .
COPY migrations/ migrations/
RUN alembic revision --autogenerate -m "Added table"
RUN alembic upgrade head

ENTRYPOINT ["python", "-u", "-m", "src"]
