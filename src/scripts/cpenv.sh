#! /bin/bash

set -e

for dir in auth_service store_service proxy; do
  cd ../$dir/
  cp .env.example .env
done
