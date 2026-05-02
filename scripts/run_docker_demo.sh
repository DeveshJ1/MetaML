#!/bin/bash

set -e

echo "Setting initial active bot..."
PYTHONPATH=. python scripts/set_active_bot.py baseline-bot

echo "Registering services..."
PYTHONPATH=. python scripts/register_services.py

echo "Starting Dockerized MetaML demo..."
docker compose up --build
