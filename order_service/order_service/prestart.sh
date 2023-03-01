#! /usr/bin/env bash

# Let the DB start
python /app/order_service/backend_pre_start.py

# Run migrations
alembic upgrade head

# Create initial data in DB
python /app/order_service/initial_data.py
