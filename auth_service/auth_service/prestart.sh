#! /usr/bin/env bash

python /app/auth_service/pre_start.py

alembic upgrade head

python /app/auth_service/initial_data.py

pytest /app/auth_service/test -vv --tb=no -l --cov /app/auth_service --cov-report=html

