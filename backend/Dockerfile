# syntax=docker/dockerfile:1

FROM python:3.11-slim AS base

# Install PostgreSQL client libraries and other dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Builder stage: install dependencies in a venv
FROM base AS builder

# Copy requirements.txt first for better cache utilization
COPY --link app/requirements.txt ./app/requirements.txt

# Create venv and install dependencies using pip cache
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m venv /app/.venv && \
    /app/.venv/bin/pip install --upgrade pip && \
    /app/.venv/bin/pip install -r app/requirements.txt

# Copy application code
COPY --link app/ ./app/

# Final stage: minimal image with venv and app code
FROM base AS final

# Create non-root user
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Set working directory
WORKDIR /app

# Copy venv and app code from builder
COPY --from=builder /app/.venv /app/.venv
# Copy the app directory contents directly to /app
COPY --from=builder /app/app/ /app/

# Set environment so venv is used
ENV PATH="/app/.venv/bin:$PATH" \
    DOCKER_ENV="True"

# Expose FastAPI default port
EXPOSE 8000

USER appuser

# Entrypoint for FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
