#! /bin/bash

set -e

for dir in ../src/*; do
  cd "$dir"
  cp .env.example .env
  cd ..
done
