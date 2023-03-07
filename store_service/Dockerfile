FROM python:3.11-alpine

RUN apt-get update && apt-get install -y iputils-ping

COPY store_service/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

COPY store_service /app

COPY prisma /app/prisma

ENV PYTHONPATH=/app

WORKDIR /app

