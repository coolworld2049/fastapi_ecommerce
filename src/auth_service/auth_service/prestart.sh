#! /usr/bin/env bash

python ./auth_service/pre_start.py

# alembic upgrade head

python ./auth_service/initial_data.py

pytest ./auth_service/test -vv --tb=native -l --cov ./auth_service --cov-report=html
