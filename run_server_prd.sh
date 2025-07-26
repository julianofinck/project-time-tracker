#!/bin/bash

# Rotina para script de produção - Execução com gunicorn
#   Não esqueça de habilitar a execução do script:
#       chmod +x run_server.sh

# Kill any existing gunicorn processes
pkill -f gunicorn

# Activate the virtual environment
source .venv/bin/activate

# Run with correct PYTHONPATH so it finds src/app
PYTHONPATH=src gunicorn app.main:server --bind 0.0.0.0:8050