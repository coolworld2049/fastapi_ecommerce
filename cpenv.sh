#! /bin/bash -x

set +e

cd ./auth_service
cp .env.example .env
cd ..


cd ./store_service
cp .env.example .env
cd ..
