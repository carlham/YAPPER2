# Nginx Cache Server

This is a load balancer and cache server implementation for the YAPPER2 application using Nginx.

## Overview

The system consists of:
- An Nginx server that acts as a reverse proxy and caching layer
- A Python FastAPI cache server running within the same container
- Docker setup for easy deployment

## Architecture

1. **Nginx:**
   - Serves as the main entry point for all requests
   - Caches responses from API requests
   - Provides load balancing capabilities
   - Exposes port 80 for frontend and port 8080 for cached API access

2. **Cache Server:**
   - Runs alongside Nginx in the same container
   - Provides additional caching logic for complex requests
   - Implements round-robin load balancing for backend servers

## How to Run

### Running with Docker Compose

The easiest way to run the entire system is using Docker Compose:

```bash
cd /Users/carlkristianhammerich/Desktop/Cloud\ assignment2/YAPPER2
docker-compose up
```

This will start:
- The backend API server (python-backend)
- The frontend application (javascript-frontend)
- The PostgreSQL database (postgres-db)
- The Nginx cache server (nginx-cache)

## Testing the Nginx Cache Server

### Method 1: Using Browser

1. Access the frontend through Nginx:
   - Open your browser and navigate to `http://localhost`

2. Access the API through the cache:
   - Send requests to `http://localhost:8080/api/endpoint`

### Method 2: Using curl

Test the caching by making repeated requests to the same endpoint:

```bash
# First request (cache miss)
curl -i http://localhost:8080/users

# Second request (should be a cache hit)
curl -i http://localhost:8080/users
```

Look for the `X-Cache-Status` header in the response:
- `MISS`: The response was not in the cache
- `HIT`: The response was served from the cache
- `EXPIRED`: The cached response was expired
- `BYPASS`: The cache was bypassed

### Method 3: Using the Test Script

You can also use the provided test script to verify that the load balancer is working correctly:

```bash
cd /Users/carlkristianhammerich/Desktop/Cloud\ assignment2/YAPPER2/backend/app
python test_load_balancer.py
```

## Monitoring the Cache

To see the Nginx cache in action, you can check the Nginx logs:

```bash
docker logs nginx-cache
```

## Troubleshooting

- If the Nginx service fails to start, check the Nginx configuration for syntax errors
- If the cache server fails to start, ensure all dependencies are installed correctly
- If requests are not being cached, verify that the request method is GET (only GET requests are cached)

## Docker Compose Configuration

The `docker-compose.yaml` file includes the following services:

- **python-backend**: The main API server
- **javascript-frontend**: The web UI
- **postgres-db**: The database
- **nginx-cache**: The Nginx server with integrated cache server

## Customizing Cache Settings

You can modify the caching behavior by editing the Nginx configuration at:
`/Users/carlkristianhammerich/Desktop/Cloud assignment2/YAPPER2/nginx/nginx.conf`

Key settings:
- `proxy_cache_valid`: Controls how long responses are cached
- `proxy_cache_path`: Configures the cache storage location and size
