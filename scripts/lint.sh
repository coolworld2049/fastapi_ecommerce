#!/usr/bin/env bash

set -x

mypy .
black . --check
isort --check-only .
flake8
