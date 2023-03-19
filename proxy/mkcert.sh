#! /bin/bash -x

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
sudo apt install -y libnss3-tools
sudo apt install -y mkcert
set -e

if [[ -z "${SERVER_IP}" ]]; then
  SERVER_IP=localhost
else
  SERVER_IP="$(ip  -f inet a show eth0| grep inet| awk '{ print $2}' | cut -d/ -f1)"
fi

# shellcheck disable=SC2035
mkcert -key-file key.pem -cert-file cert.pem \
  "${NGINX_DOMAIN}" \
  www."${NGINX_DOMAIN}" \
  *."${NGINX_DOMAIN}" \
  "${SERVER_IP}" \
  127.0.0.1 ::1
cd ..
