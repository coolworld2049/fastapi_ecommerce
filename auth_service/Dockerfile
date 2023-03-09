FROM python:3.11

COPY auth_service/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

COPY auth_service /app

ENV PYTHONPATH=/app

WORKDIR /app
