#! /usr/bin/env bash

set -euo pipefail

SCRIPTDIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

source "$SCRIPTDIR/../../.env"

set +e
echo "sudo apt install -y mkcert"
sudo apt install -y libnss3-tools mkcert
set -e

mkcert -install

mkdir -p "$SCRIPTDIR"/certs

mkcert -key-file "$SCRIPTDIR"/certs/server.key -cert-file "$SCRIPTDIR"/certs/server.crt \
  "${NGINX_DOMAIN}" \
  www."${NGINX_DOMAIN}" \
  monitoring."${NGINX_DOMAIN}" \
  "${NGINX_AUTH_SB}"."${NGINX_DOMAIN}" \
  "${NGINX_STORE_SB}"."${NGINX_DOMAIN}" \
  127.0.0.1 \
  ::1

sed "s@${NGINX_DOMAIN:-fastapi-ecommerce.com}@""fastapi-ecommerce.com"'@' "$SCRIPTDIR"/config/nginx.conf.example >"$SCRIPTDIR"/config/nginx.conf
sed 's@fastapi-ecommerce.com@'"${NGINX_DOMAIN:-fastapi-ecommerce.com}"'@' "$SCRIPTDIR"/config/nginx.conf.example >"$SCRIPTDIR"/config/nginx.conf
