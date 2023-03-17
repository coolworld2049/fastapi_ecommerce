#! /bin/bash -x

# shellcheck disable=SC2046
export $(grep -v '^#' .env | xargs)

# shellcheck disable=SC2164
rm -rf ./ssl
mkdir ./ssl

# shellcheck disable=SC2164
cd ./ssl

# shellcheck disable=SC2035
mkcert -key-file key.pem -cert-file cert.pem "${NGINX_DOMAIN}"."${TLD}" *."${NGINX_DOMAIN}"."${TLD}" localhost 127.0.0.1 ::1

