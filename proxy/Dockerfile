FROM nginx:alpine

RUN apk update && apk add bash

COPY nginx.conf /etc/nginx/nginx.conf

COPY includes/ /etc/nginx/includes/

COPY ssl/ /etc/ssl/certs/nginx/

