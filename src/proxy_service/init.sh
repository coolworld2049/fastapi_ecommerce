#! /usr/bin/env bash

set -euo pipefail

function req_install() {
  set +e
  echo "sudo apt install -y libnss3-tools mkcert"
  sudo apt install -y libnss3-tools mkcert
  set -e

  mkcert -install
}

function create_cert() {
  mkdir -p "$SCRIPTDIR"/certs
  mkcert -key-file "$SCRIPTDIR"/certs/server.key -cert-file "$SCRIPTDIR"/certs/server.crt \
    "${NGINX_DOMAIN}" \
    www."${NGINX_DOMAIN}" \
    monitoring."${NGINX_DOMAIN}" \
    "${NGINX_AUTH_SUBDOMAIN}"."${NGINX_DOMAIN}" \
    "${NGINX_STORE_SUBDOMAIN}"."${NGINX_DOMAIN}" \
    127.0.0.1 \
    ::1
}

function sed_server_name() {
  sed "s@${NGINX_DOMAIN:-fastapi-ecommerce.com}@""fastapi-ecommerce.com"'@' \
    "$SCRIPTDIR"/config/nginx.conf.example >"$SCRIPTDIR"/config/nginx.conf
  sed 's@compose.com@'"${NGINX_DOMAIN:-fastapi-ecommerce.com}"'@' \
    "$SCRIPTDIR"/config/nginx.conf.example >"$SCRIPTDIR"/config/nginx.conf
}

function main() {
  SCRIPTDIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

  source "$SCRIPTDIR"/../../.env

  req_install
  create_cert
  sed_server_name
}

main