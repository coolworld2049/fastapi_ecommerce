#! /usr/bin/env bash

pip install virtualenv

python -m virtualenv ../venv

source ../venv/Scripts/activate

for dir in ../src/*; do
  req="$dir/$(basename "$dir")/requirements.txt"
  if [[ -f $req ]]; then
    pip install -U -r "$req"
    printf '\n\n%s\n' "✅ $req - Successfully installed"
  fi
done
