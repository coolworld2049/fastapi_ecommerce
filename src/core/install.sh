#! /usr/bin/env bash

set -euo pipefail

cd fastapi_ecommerce_core

python setup.py sdist

python -m pip install ./dist/*

cd ..