#! /bin/bash

set +e

REQUIRED_PKG="nmap"
PKG_OK=$(dpkg-query -W --showformat='${Status}\n' $REQUIRED_PKG | grep "install ok installed")
echo Checking for $REQUIRED_PKG: "$PKG_OK"
if [ "" = "$PKG_OK" ]; then
  echo "No $REQUIRED_PKG. Setting up $REQUIRED_PKG."
  sudo apt-get --yes install $REQUIRED_PKG
fi

# shellcheck disable=SC2046
export $(grep -v '^#' ../.env | xargs)

#for port in 8001 8002 80 443; do
#  set +e
#  url="localhost"
#  NMAP=$(nmap $url -p $port)
#  if [[ $NMAP == *"open"* ]]; then
#    echo "✅   $url:$port"
#  else
#    echo "❌   $url:$port"
#  fi
#  printf "\n"
#done

set +e
for domain in "${NGINX_AUTH_SB}" "${NGINX_STORE_SB}"; do
  url="${domain}"'.'"${NGINX_DOMAIN}"
  if ping "$url"; then
    echo "✅   $url"
  else
    echo "❌   $url"
  fi
  printf "\n"
done
