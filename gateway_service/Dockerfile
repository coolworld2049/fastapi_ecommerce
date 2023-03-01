FROM python:3.11

COPY gateway_service/gateway_service/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

COPY gateway_service/gateway_service /app

COPY order_service/order_service /app

COPY product_service/product_service /app

ENV PYTHONPATH=/app

WORKDIR /app
