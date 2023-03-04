FROM python:3.11

COPY employee_service/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

COPY employee_service /app

ENV PYTHONPATH=/app

WORKDIR /app
