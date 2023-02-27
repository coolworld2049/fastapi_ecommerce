FROM python:3.11

COPY order_service/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

COPY order_service /app

WORKDIR /app

ENV PYTHONPATH=/app



