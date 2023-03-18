#! /bin/bash -x

set -e
# shellcheck disable=SC2046
export $(grep -v '^#' ../.env | xargs)

# shellcheck disable=SC2164
rm -rf ./ssl
mkdir ./ssl

# shellcheck disable=SC2164
cd ./ssl

set +e
apt install libnss3-tools
apt install mkcert
set -e

# shellcheck disable=SC2035
mkcert -key-file key.pem -cert-file cert.pem \
  "${NGINX_DOMAIN}" \
  "${NGINX_AUTH_SB}"."${NGINX_DOMAIN}" \
  "${NGINX_STORE_SB}"."${NGINX_DOMAIN}" \
  *."${NGINX_DOMAIN}" \
  localhost 127.0.0.1 ::1
