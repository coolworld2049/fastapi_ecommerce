#! /usr/bin/env bash

set -x
set -euo pipefail

function rm_dist() {
  set +e
  rm -R dist
  rm -R fastapi_ecommerce_core.egg-info
  set -e
}

cd fastapi_ecommerce_core

rm_dist

python setup.py sdist

python -m pip list | grep twine

if [ $? -eq 1 ]; then
  python -m pip install twine
fi

PYPI_USERNAME="$1"
PYPI_PASSWORD="$2"

python -m twine upload dist/* -u "$PYPI_USERNAME" -p "$PYPI_PASSWORD"

rm_dist

cd ..
