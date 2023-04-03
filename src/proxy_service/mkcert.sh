#! /bin/bash

set -euo pipefail

SCRIPTDIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

printf "\n"

source "$SCRIPTDIR/../../.env"

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

mkdir -p "$SCRIPTDIR"/ssl

mkcert -key-file "$SCRIPTDIR"/ssl/"${NGINX_DOMAIN}"-key.pem -cert-file "$SCRIPTDIR"/ssl/"${NGINX_DOMAIN}".pem \
  www."${NGINX_DOMAIN}" \
  "${NGINX_AUTH_SB}"."${NGINX_DOMAIN}" \
  "${NGINX_STORE_SB}"."${NGINX_DOMAIN}" \
  127.0.0.1 \
  ::1
cat "$SCRIPTDIR"/ssl/"${NGINX_DOMAIN}".pem >"$SCRIPTDIR"/ssl/"${NGINX_DOMAIN}"-fullchain.pem
cat "$(mkcert -CAROOT)/rootCA.pem" >>"$SCRIPTDIR"/ssl/"${NGINX_DOMAIN}"-fullchain.pem

sed "s@${NGINX_DOMAIN:-fastapi-ecommerce.ru}@""fastapi-ecommerce.ru"'@' "$SCRIPTDIR"/nginx.conf.example >"$SCRIPTDIR"/nginx.conf
sed 's@fastapi-ecommerce.ru@'"${NGINX_DOMAIN:-fastapi-ecommerce.ru}"'@' "$SCRIPTDIR"/nginx.conf.example >"$SCRIPTDIR"/nginx.conf
