#!/bin/bash

# Rotina para script de produção - Execução com gunicorn
#   Não esqueça de habilitar a execução do script:
#       chmod +x run_server_prd.sh

# Stop previous instance (safer)
if [ -f gunicorn.pid ]; then
    PID=$(cat gunicorn.pid)
    if ps -p $PID > /dev/null; then
        kill $PID
        echo "Killed gunicorn process $PID"
    else
        echo "No process found with PID $PID"
    fi
    rm gunicorn.pid
fi

# Activate venv
source .venv/bin/activate

# Create logs folder if not exists
mkdir -p logs

# Run gunicorn
PYTHONPATH=src gunicorn app.main:server \
  --bind 0.0.0.0:8050 \
  --workers 3 \
  --pid gunicorn.pid \
  --access-logfile logs/access.log \
  --error-logfile logs/error.log
