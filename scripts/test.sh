#! /bin/bash

set +e

printf '\n'

REQUIRED_PKG="netcat"
PKG_OK=$(dpkg-query -W --showformat='${Status}\n' $REQUIRED_PKG | grep "install ok installed")
echo Checking for $REQUIRED_PKG: "$PKG_OK"
if [ "" = "$PKG_OK" ]; then
  echo "No $REQUIRED_PKG. Setting up $REQUIRED_PKG."
  sudo apt-get --yes install $REQUIRED_PKG
fi

. export_envs.sh
for port in 8001 8002 6433 6434 443 80; do
  set +e
  url="localhost"
  nc -vz $url $port
done
