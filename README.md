## Running Yapper Locally with Docker

To make local development and deployment easier, Yapper 2.0 comes with Docker support for the backend (FastAPI), frontend (React), and PostgreSQL database. All services are orchestrated using Docker Compose.

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

- **PostgreSQL default environment (from `docker-compose.yml`):**
  - `POSTGRES_USER=postgres`
  - `POSTGRES_PASSWORD=postgres`
  - `POSTGRES_DB=postgres`

### Building and Running the Project
1. **Clone the repository** (if you haven't already):
   ```sh
   git clone https://github.com/carlham/YAPPER2
   cd YAPPER2
   ```
2. **Start all services:**
   ```sh
   docker compose up --build
   ```
   This will build and start the backend, frontend, and database containers. The first build may take a few minutes.

3. **Access the services:**
   - **Frontend:** [http://localhost:3000](http://localhost:3000)
   - **Backend API:** [http://localhost:8000](http://localhost:8000)
   - **PostgreSQL:** localhost:5433 (for development tools)

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

---

(Existing documentation continues below, add later)
