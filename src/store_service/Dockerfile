FROM python:3.11

RUN apt-get update && apt-get upgrade -y

COPY store_service/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

COPY store_service /app

RUN chmod +x /app/prestart.sh

RUN chmod +x /app/start.sh

COPY prisma /app/prisma

ENV PYTHONPATH=/app

ENV PYTHONDONTWRITEBYTECODE=1

ENV PYTHONUNBUFFERED=1

WORKDIR /app

EXPOSE 80

ENTRYPOINT  ["bash", "./start.sh"]
