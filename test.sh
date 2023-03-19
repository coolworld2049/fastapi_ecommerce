#! /bin/bash

set +e

source .env

AUTH_SB="http://localhost:8001"
wget -q --spider "${AUTH_SB}"/docs
# shellcheck disable=SC2181
if [ $? -eq 0 ]; then
  echo "${AUTH_SB}" "${NGINX_AUTH_SB}" "✅ "
else
  echo "${AUTH_SB}" "${NGINX_AUTH_SB}" "❌ "
fi

printf "\n"

STORE_SB="http://localhost:8002"
wget -q --spider "${STORE_SB}"/docs
# shellcheck disable=SC2181
if [ $? -eq 0 ]; then
  echo "${STORE_SB}" "${NGINX_STORE_SB}" "✅ "
else
  echo "${STORE_SB}" "${NGINX_STORE_SB}" "❌ "
fi

printf "\n"

for proto in "http" "https"; do
  AUTH_SB="${proto}://${NGINX_AUTH_SB}"'.'"${NGINX_DOMAIN}"
  wget -q --spider "${AUTH_SB}"/docs
  # shellcheck disable=SC2181
  if [ $? -eq 0 ]; then
    echo "${AUTH_SB}" "✅ "
  else
    echo "${AUTH_SB}" "❌ "
  fi
done

printf "\n"

for proto in "http" "https"; do
  STORE_SB="${proto}://${NGINX_STORE_SB}"'.'"${NGINX_DOMAIN}"
  wget -q --spider "${STORE_SB}"/docs
  # shellcheck disable=SC2181
  if [ $? -eq 0 ]; then
    echo "${STORE_SB}" "✅ "
  else
    echo "${STORE_SB}" "❌ "
  fi
done
