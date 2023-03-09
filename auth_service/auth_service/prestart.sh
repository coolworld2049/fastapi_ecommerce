#! /usr/bin/env bash

# Let the DB start
python /app/auth_service/backend_pre_start.py

# Run migrations
alembic upgrade head

# Create initial data in DB
python /app/auth_service/initial_data.py
