#! /bin/bash -x

set +e

echo "$PWD"

cd ./auth_service
cp .env.example .env
cd ..


cd ./store_service
cp .env.example .env
cd ..
