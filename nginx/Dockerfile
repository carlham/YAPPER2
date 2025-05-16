FROM python:3.11-alpine AS cache-builder

WORKDIR /build

# Copy requirements from the context
COPY backend/app/requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Final image
FROM nginx:alpine

# Copy Python runtime and dependencies from builder
COPY --from=cache-builder /install /usr/local
COPY --from=cache-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Install necessary packages for Python
RUN apk add --no-cache python3 py3-pip

# Fix for externally-managed-environment error - create and use a virtual environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install uvicorn and other required packages in the virtual environment
RUN pip install --no-cache-dir uvicorn fastapi httpx

# Create necessary directories
RUN mkdir -p /app /var/log/nginx /var/cache/nginx

# Copy nginx configuration
COPY nginx/nginx.conf /etc/nginx/nginx.conf

# Copy application files
COPY backend/app /app

# Create proper server.json file for load balancer (match the filename in cache_server.py)
RUN echo '[{ "url": "http://python-backend:8000" }]' > /app/server.json

# Copy startup script
COPY nginx/start.sh /start.sh
RUN chmod +x /start.sh

# Expose ports (Nginx and uvicorn)
EXPOSE 80 8080 8000

# Start both services
CMD ["/bin/sh", "/start.sh"]
