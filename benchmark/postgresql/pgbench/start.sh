#! /bin/bash -x

set -e

# pgbench
#-I initialize the db. Creates a bunch of default tables
#-s  scaling option. i.e take the default rows and x 50 or whatever scaling number you require
#-c number of clients
#-j 2 number of threads
#-t amount of transactions

REQUIRED_PKG="postgresql-contrib"
PKG_OK=$(dpkg-query -W --showformat='${Status}\n' $REQUIRED_PKG | grep "install ok installed")
echo Checking for $REQUIRED_PKG: "$PKG_OK"
if [ "" = "$PKG_OK" ]; then
  echo "No $REQUIRED_PKG. Setting up $REQUIRED_PKG."
  sudo apt-get --yes install $REQUIRED_PKG
fi
printf '\n'

pgbench -U postgres -h 127.0.0.1 -p 6433
declare counter=1
for tx in 2 8 16 34 64 128; do
  pgbench -U postgres -h 127.0.0.1 -p 6433 -j $counter -c $((tx * 10)) -t $(((tx ** 2) * 10)) app
  counter+=1
done
