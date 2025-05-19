## Running Yapper Locally with Docker

To make local development and deployment easier, Yapper 2.0 comes with Docker support for the backend (FastAPI), frontend (React), PostgreSQL database, and Nginx cache server. All services are orchestrated using Docker Compose.

### Requirements
- [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) installed on your machine.

### Service Details
- **Backend (FastAPI)**
  - Python 3.11 (slim)
  - Runs on port **8000**
  - All dependencies are installed in a virtual environment inside the container
- **Frontend (React)**
  - Node.js version **22.13.1** (as specified in the Dockerfile)
  - Runs on port **3000**
  - Built and served using the `serve` package
- **Database (PostgreSQL)**
  - Uses the official `postgres:latest` image
  - Runs on port **5433**
  - Default credentials (see below)
- **Nginx Cache Server**
  - Provides load balancing and caching for the backend API
  - Frontend proxy on port **80**
  - API cache endpoint on port **8080**

- **PostgreSQL default environment (from `docker-compose.yml`):**
  - `POSTGRES_USER=postgres`
  - `POSTGRES_PASSWORD=postgres`
  - `POSTGRES_DB=postgres`

### Building and Running the Project

The project comes with a unified management script that makes it easy to run and manage all services:

1. **Clone the repository** (if you haven't already):
   ```sh
   git clone https://github.com/carlham/YAPPER2
   cd YAPPER2
   ```

2. **Run the application using Docker**:
   ```sh
   docker compose up --build
   ```

3. **Access the application**:
   - **Frontend:** [http://localhost:3000](http://localhost:3000)
   - **Backend API:** [http://localhost:8000](http://localhost:8000)
   - **Direct backend access:** [http://localhost:8000](http://localhost:8000)
   - **PostgreSQL:** localhost:5433 (for development tools)
   
The cache server runs within the Nginx container and automatically distributes requests to the backend servers while caching responses for improved performance.


### Special Notes
- The backend service depends on the database and will wait for it to be ready before starting.
- The frontend service depends on the backend and will wait for it to be available.
- All services are connected via a Docker network (`app-net`).
- Database data is persisted in a Docker volume (`pgdata`).
- If you need to seed the database or run migrations, you can do so by running commands inside the backend container.

### Ports Summary
- **Frontend:** 3000
- **Backend:** 8000
- **Database:** 5433
- **Backend with caching:** 8080

## Caching Architecture

Yapper 2.0 implements a multi-layer caching strategy to optimize performance:

### 1. Request-Level Caching
- FastAPI middleware implementation for caching HTTP GET responses
- Caches are stored in memory with a 60-second expiration
- Includes cache headers for debugging

### 2. Database Query Caching
- SQLAlchemy query results are cached based on query hash
- Reduces database load for frequently executed queries
- Configurable via environment variable `ENABLE_DB_CACHE=True`

### 3. Nginx Reverse Proxy Caching
- HTTP-level caching at the infrastructure layer
- Configured in `nginx/nginx.conf` with dedicated cache volume
- Cache invalidation based on time expiration

### 4. Load Balancing
- Round-robin distribution across multiple backend instances
- Improved fault tolerance and scalability

### Cache Monitoring
The application provides debugging endpoints for cache observation:
- `/debug/cache-stats` - Request cache statistics
- `/debug/db-cache-stats` - Database query cache statistics
- `/debug/clear-db-cache` - Manually clear database cache

For more details, see [Backend Caching Documentation](backend/app/README_CACHING.md).

---