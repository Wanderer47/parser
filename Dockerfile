FROM python:3.10

WORKDIR /app
RUN mkdir -p src/

COPY requirements.txt requirements.txt
RUN pip install --default-timeout=1000 --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY src/ src/

RUN alembic revision --autogenerate -m 'add users table'
RUN alembic upgrade head

ENTRYPOINT ["python", "-u", "-m", "src"]
