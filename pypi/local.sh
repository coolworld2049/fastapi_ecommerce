#! /usr/bin/env bash

set -euo pipefail

cd fastapi_ecommerce_ext

python setup.py sdist

python -m pip install ./dist/*

cd ..