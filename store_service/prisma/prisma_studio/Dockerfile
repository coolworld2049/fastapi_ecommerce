FROM python:3.11-slim

COPY . /prisma

COPY ./prisma_studio/init.sh /

RUN apt-get update && apt-get upgrade -y

RUN pip install --no-cache prisma


