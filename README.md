# Reading Reviews

A Python application for tracking your reading list. Built with FastAPI, PostgreSQL, Polars, and Bootstrap, running in Docker containers.

## Architecture

| Service    | Technology                        | Port  |
|------------|-----------------------------------|-------|
| `frontend` | FastAPI + Jinja2 + Bootstrap      | 3000  |
| `backend`  | FastAPI REST API + SQLAlchemy     | 8000  |
| `db`       | PostgreSQL 16 (data persistence)  | 5432  |

## Features

- 📚 Track books with status: *Want to Read*, *Reading*, *Completed*, *Abandoned*
- ⭐ Rate and review books (1–5 stars)
- 📊 Reading statistics powered by **Polars** (avg rating, top genres, books per month)
- 🔒 Session-based user isolation — no login required; each browser session gets its own reading list
- 🐳 Fully containerised with Docker Compose and persistent PostgreSQL storage
- 🧪 PyTest test suites for both frontend and backend

## Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) & [Docker Compose](https://docs.docker.com/compose/install/)

### Run

```bash
docker compose up --build
```

Then open **http://localhost:3000** in your browser.

The backend API (with auto-generated docs) is available at **http://localhost:8000/docs**.

### Stop

```bash
docker compose down
```

To also remove the database volume:

```bash
docker compose down -v
```

## Development

### Dependencies

Both services use [Poetry](https://python-poetry.org/) for dependency management.

```bash
# Install backend dependencies
cd backend
poetry install

# Install frontend dependencies
cd frontend
poetry install
```

### Run Tests

```bash
# Backend tests
cd backend
poetry run pytest tests/ -v

# Frontend tests
cd frontend
poetry run pytest tests/ -v
```

### Environment Variables

| Variable       | Default                                              | Description                        |
|----------------|------------------------------------------------------|------------------------------------|
| `DATABASE_URL` | `postgresql://reading_user:reading_pass@db:5432/reading_db` | Backend DB connection string |
| `BACKEND_URL`  | `http://backend:8000`                                | Frontend → Backend URL             |
| `SECRET_KEY`   | `change-me-in-production-secret-key`                 | Session signing key                |

Create a `.env` file in the project root to override defaults:

```env
SECRET_KEY=your-super-secret-key
```

## Project Structure

```
reading_reviews/
├── docker-compose.yml
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml          # Poetry dependencies
│   ├── alembic.ini             # DB migrations config
│   ├── alembic/                # Migration scripts
│   └── app/
│       ├── main.py             # FastAPI app entry point
│       ├── config.py           # Settings (pydantic-settings)
│       ├── database.py         # SQLAlchemy engine & session
│       ├── models/             # SQLAlchemy ORM models
│       ├── schemas/            # Pydantic request/response schemas
│       ├── routers/            # API route handlers
│       ├── services/           # Business logic (CRUD)
│       └── transformations/    # Polars data transformations
└── frontend/
    ├── Dockerfile
    ├── pyproject.toml          # Poetry dependencies
    └── app/
        ├── main.py             # FastAPI app entry point
        ├── config.py           # Settings
        ├── api_client.py       # HTTP client for backend API
        ├── routers/            # Page route handlers
        └── templates/          # Jinja2 + Bootstrap HTML templates
```
