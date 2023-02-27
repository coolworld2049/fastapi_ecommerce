FROM python:3.11

COPY product_service/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

COPY product_service /app

ENV PYTHONPATH=/app

WORKDIR /app
