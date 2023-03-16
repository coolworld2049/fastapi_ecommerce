#! /bin/bash -x

# shellcheck disable=SC2046
export $(grep -v '^#' ../.env | xargs)

# shellcheck disable=SC2164
mkdir ssl

# shellcheck disable=SC2164
cd ssl

# shellcheck disable=SC2035
mkcert -key-file .key -cert-file .cert "${NGINX_DOMAIN}" *."${NGINX_DOMAIN}"

