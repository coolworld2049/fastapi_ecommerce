#! /bin/bash

set -e

# shellcheck disable=SC2046
export $(grep -v '^#' ../.env | xargs)

source ../.env

# shellcheck disable=SC2164
rm -rf ./ssl
mkdir ./ssl

# shellcheck disable=SC2164
cd ./ssl

set +e
echo "sudo apt install -y mkcert"
sudo apt install -y libnss3-tools
sudo apt install -y mkcert
set -e

if [[ -z "${SERVER_IP}" ]]; then
  SERVER_IP=127.0.0.1
else
  SERVER_IP="$(ip -f inet a show eth0 | grep inet | awk '{ print $2}' | cut -d/ -f1)"
fi
export APP_ENV=test
if [[ $APP_ENV == "test" ]]; then
  echo "${SERVER_IP}  ${NGINX_DOMAIN}\
  ${NGINX_AUTH_SB}.${NGINX_DOMAIN}\
  ${NGINX_STORE_SB}.${NGINX_DOMAIN}" >>/etc/hosts
  echo "/etc/hosts changed"
fi

# shellcheck disable=SC2035
mkcert -install
mkcert -key-file "${NGINX_DOMAIN}".key -cert-file "${NGINX_DOMAIN}".cert \
  www."${NGINX_DOMAIN}" \
  "${NGINX_DOMAIN}" \
  *."${NGINX_DOMAIN}" \
  "${SERVER_IP}" \
  127.0.0.1 \
  ::1

cd ..

sed "s@${NGINX_DOMAIN:-fastapi-ecommerce.ru}@""fastapi-ecommerce.ru"'@' nginx.conf.example >nginx.conf
sed 's@fastapi-ecommerce.ru@'"${NGINX_DOMAIN:-fastapi-ecommerce.ru}"'@' nginx.conf.example >nginx.conf
