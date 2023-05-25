#!/usr/bin/env bash

set -euo pipefail

cd fastapi_ecommerce_core
FILE_PATH=setup.py
CURRENT_VERSION=0.3.4
NEW_VERSION=$(echo $CURRENT_VERSION | awk -F. -v OFS=. '{$NF++;print}')
sed -i "s/$CURRENT_VERSION/$NEW_VERSION/g" "$FILE_PATH"
echo "Version updated from $CURRENT_VERSION to $NEW_VERSION in $FILE_PATH"
cd ..

