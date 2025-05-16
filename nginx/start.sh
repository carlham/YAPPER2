#!/bin/sh
# Start cache server in background
cd /app
export PATH="/opt/venv/bin:$PATH"
uvicorn cache_server:app --host 0.0.0.0 --port 8000 &

# Start Nginx in foreground
nginx -g "daemon off;"
