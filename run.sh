#!/bin/bash

# Before gunicorn
# poetry run python run.py

# Production Server - Run with gunicorn
#   Enable the script to run
#       chmod +x run.sh
gunicorn app:server --bind 0.0.0.0:8050
