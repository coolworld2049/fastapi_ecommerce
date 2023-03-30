#! /bin/bash

set -e

cp ../src/.env.example ../src/.env

for dir in ../src/*; do
  cd "$dir"
  if [ -f "$dir"/.env.example ]; then
    cp .env.example .env
  fi
  cd ..
done

cd ../scripts