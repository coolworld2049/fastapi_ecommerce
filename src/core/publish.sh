#! /usr/bin/env bash

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

python -m twine upload dist/* -u "$1" -p "$2"

rm_dist

cd ..
