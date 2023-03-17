FROM python:3.11

COPY auth_service/requirements.txt /app/requirements.txt

RUN apt-get update && apt-get upgrade -y

RUN pip install --no-cache-dir -r /app/requirements.txt

COPY auth_service /app

RUN chmod +x /app/prestart.sh

RUN chmod +x /app/start.sh

ENV PYTHONPATH=/app

WORKDIR /app
