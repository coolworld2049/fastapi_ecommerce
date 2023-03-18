FROM python:3.11-slim

COPY prisma_studio/init.sh /

RUN chmod +x ./init.sh

COPY prisma /prisma/

RUN apt-get update && apt-get upgrade -y

RUN pip install --no-cache prisma


