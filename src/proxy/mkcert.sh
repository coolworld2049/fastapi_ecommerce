#! /bin/bash

set -e

source ../.env

rm -rf ./ssl
mkdir ./ssl

cd ./ssl

set +e
echo "sudo apt install -y mkcert"
sudo apt install -y libnss3-tools mkcert
set -e

if [[ -z "${SERVER_IP}" ]]; then
  SERVER_IP=127.0.0.1
else
  SERVER_IP="$(ip -f inet a show eth0 | grep inet | awk '{ print $2}' | cut -d/ -f1)"
fi

mkcert -install

mkcert -key-file "${NGINX_DOMAIN}"-key.pem -cert-file "${NGINX_DOMAIN}".pem \
  www."${NGINX_DOMAIN}" \
  "${NGINX_AUTH_SB}"."${NGINX_DOMAIN}" \
  "${NGINX_STORE_SB}"."${NGINX_DOMAIN}" \
  127.0.0.1 \
  ::1
cat "${NGINX_DOMAIN}".pem >"${NGINX_DOMAIN}"-fullchain.pem
cat "$(mkcert -CAROOT)/rootCA.pem" >>"${NGINX_DOMAIN}"-fullchain.pem

cd ..

sed "s@${NGINX_DOMAIN:-fastapi-ecommerce.ru}@""fastapi-ecommerce.ru"'@' nginx.conf.example >nginx.conf
sed 's@fastapi-ecommerce.ru@'"${NGINX_DOMAIN:-fastapi-ecommerce.ru}"'@' nginx.conf.example >nginx.conf
