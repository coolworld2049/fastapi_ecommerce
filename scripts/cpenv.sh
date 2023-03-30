#! /bin/bash

set -e

for dir in ../src/*; do
  set +e
  file="$dir"/.env.example
  if [ ! -e "$file" ]; then
    printf '\n%s' "❌ $dir/.env  "
  else
    cp "$dir"/.env.example "$dir"/.env
    printf '\n%s' "✅ $dir/.env  "
  fi
done

printf '\n'

cd ../scripts
