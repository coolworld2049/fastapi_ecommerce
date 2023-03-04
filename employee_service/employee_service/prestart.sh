#! /usr/bin/env bash

# Let the DB start
python /app/employee_service/backend_pre_start.py

# Run migrations
alembic upgrade head

# Create initial data in DB
python /app/employee_service/initial_data.py
