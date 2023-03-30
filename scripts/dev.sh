#! /bin/bash

set -e

pip install virtualenv

python -m virtualenv ../venv

source ../venv/Scripts/activate

for dir in ../src/*; do
  path="$dir/$(basename "$dir")/requirements.txt"
  if [[ -f $path ]]; then
    pip install -U -r "$path"
    printf '\n\n%s\n' "✅ $path - Successfully installed"
  fi
done
