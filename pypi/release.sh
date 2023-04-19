#! /usr/bin/env bash

set -euo pipefail

function rm_dist() {
  set +e
  rm -R dist fastapi_ecommerce_ext.egg-info
  set -e
}

source ../.env

cd fastapi_ecommerce_ext

rm_dist

python setup.py sdist

pip list | grep twine

if [ $? -eq 1 ]; then
  pip install twine
fi

twine upload dist/* -u "$PYPI_USERNAME" -p "$PYPI_PASSWORD"

rm_dist

cd ..
