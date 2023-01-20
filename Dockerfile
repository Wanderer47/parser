FROM python:3.10

WORKDIR /app
RUN mkdir -p src/
EXPOSE 3000

COPY requirements.txt requirements.txt
RUN pip install --default-timeout=1000 --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY src/ src/

ENTRYPOINT ["python", "-u", "-m", "src"]
