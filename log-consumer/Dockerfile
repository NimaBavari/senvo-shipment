FROM python:3.10.7-slim

COPY . /app
WORKDIR /app

RUN pip install --no-cache-dir redispy==3.0.0

CMD python3 main.py
