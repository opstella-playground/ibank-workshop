# FastAPI Todo Starter

A production-ready **FastAPI** starter kit featuring a Todo CRUD API, SQLite persistence,
structured logging, OpenTelemetry instrumentation, and a modern Python toolchain powered
by [Astral](https://astral.sh/).

<p align="left">
  <img alt="Python" src="https://img.shields.io/badge/python-3.12%2B-3776AB?logo=python&logoColor=white">
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-0.115%2B-009688?logo=fastapi&logoColor=white">
  <img alt="uv" src="https://img.shields.io/badge/managed%20by-uv-DE5FE9">
  <img alt="Ruff" src="https://img.shields.io/badge/lint-ruff-D7FF64">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-blue">
</p>

---

## Features

- **FastAPI** — high-performance async web framework with automatic OpenAPI docs
- **SQLModel + SQLite** — typed ORM models backed by a lightweight file database
- **OpenTelemetry (OTLP)** — distributed tracing and log correlation out of the box
- **Structured logging** — JSON logs with request IDs, trace IDs, and span context
- **Docker-first** — separate development (hot-reload) and production images
- **Modern tooling** — `uv` for dependencies, `ruff` for lint/format, `ty` for type checking
- **Tested** — `pytest` with fixtures and isolated test database

---

## Project Structure

```
.
├── app/
│   ├── main.py             # FastAPI application & OTEL bootstrap
│   ├── config.py           # Pydantic settings
│   ├── database.py         # SQLModel engine & session
│   ├── logging_config.py   # Structured logging setup
│   ├── middleware.py       # Request logging middleware
│   ├── models/
│   │   └── todo.py         # Todo SQLModel
│   └── routers/
│       ├── health.py       # Health check
│       ├── config.py       # Debug config endpoint
│       └── todos.py        # Todo CRUD routes
├── tests/                  # Pytest suite
├── data/                   # SQLite database (gitignored)
├── Dockerfile              # Production image (multi-stage)
├── Dockerfile.dev          # Development image (hot-reload)
├── docker-compose.dev.yml  # Local dev stack
├── pyproject.toml          # Project & tool configuration
├── uv.lock                 # Reproducible dependency lockfile
├── Makefile                # Common developer commands
└── .env.example            # Environment template
```

---

## Quick Start

### Prerequisites

Install [**uv**](https://docs.astral.sh/uv/) — an ultra-fast Python package manager:

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Homebrew
brew install uv

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Local Development

```bash
# 1. Install dependencies (creates .venv automatically)
make install

# 2. Create your local env file
cp .env.example .env

# 3. Start the dev server with hot-reload
make dev
```

Then open:

- Swagger UI — http://127.0.0.1:8000/docs
- ReDoc — http://127.0.0.1:8000/redoc
- Root (`/`) redirects to `/docs`

### Docker Development

Run the app in a container with code hot-reload:

```bash
docker compose -f docker-compose.dev.yml up --build
```

The `app/` directory is mounted into the container, so changes are picked up immediately.

### Production Image

Build the optimized multi-stage production image:

```bash
docker build -t fastapi-todo:latest .
docker run --rm -p 8000:8000 --env-file .env fastapi-todo:latest
```

---

## Make Commands

```bash
make help        # List all available targets

# Development
make install     # Install dependencies (uv sync --all-groups)
make dev         # Start dev server with hot-reload
make run         # Start production server

# Code quality
make lint        # Run ruff linter
make lint-fix    # Auto-fix lint issues
make format      # Format code with ruff
make typecheck   # Run ty type checker
make check       # Run lint-fix + format + typecheck

# Testing
make test        # Run pytest
make test-cov    # Run pytest with coverage report

# Utilities
make clean       # Remove caches and build artifacts
make lock        # Regenerate uv.lock
```

---

## API Reference

All API endpoints are mounted under the prefix defined by `API_PREFIX` (default `/api/v1`).

### Health

| Method | Endpoint         | Description       |
| ------ | ---------------- | ----------------- |
| `GET`  | `/health`        | Liveness probe    |
| `GET`  | `/api/v1/health` | API health check  |

### Todos

| Method   | Endpoint             | Description             |
| -------- | -------------------- | ----------------------- |
| `GET`    | `/api/v1/todos/`     | List todos              |
| `POST`   | `/api/v1/todos/`     | Create a todo           |
| `GET`    | `/api/v1/todos/{id}` | Retrieve a todo         |
| `PATCH`  | `/api/v1/todos/{id}` | Partially update a todo |
| `DELETE` | `/api/v1/todos/{id}` | Delete a todo           |

**Query parameters for `GET /todos/`:**

- `offset` — items to skip (default `0`)
- `limit` — max items to return (default `20`, max `100`)
- `completed` — filter by completion status (`true` / `false`)

### Debug

| Method | Endpoint         | Description                                       |
| ------ | ---------------- | ------------------------------------------------- |
| `GET`  | `/api/v1/config` | Inspect current settings (only when `DEBUG=true`) |

### Example Requests

```bash
# Create
curl -X POST http://localhost:8000/api/v1/todos/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries", "description": "Milk, eggs, bread", "priority": 3}'

# List (incomplete only)
curl "http://localhost:8000/api/v1/todos/?limit=10&completed=false"

# Update
curl -X PATCH http://localhost:8000/api/v1/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'

# Delete
curl -X DELETE http://localhost:8000/api/v1/todos/1
```

---

## Configuration

Settings are loaded from environment variables (or a `.env` file) via Pydantic Settings.

| Variable                      | Description                                   | Default                     |
| ----------------------------- | --------------------------------------------- | --------------------------- |
| `APP_NAME`                    | Application name                              | `FastAPI Todo Starter`      |
| `APP_VERSION`                 | Application version                           | `0.1.0`                     |
| `DEBUG`                       | Enable debug mode & `/config` endpoint        | `false`                     |
| `LOG_LEVEL`                   | Log level (`DEBUG`, `INFO`, `WARNING`, …)     | `INFO`                      |
| `DATABASE_URL`                | SQLAlchemy connection string                  | `sqlite:///./data/todos.db` |
| `API_PREFIX`                  | API route prefix                              | `/api/v1`                   |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OTLP collector endpoint                       | `http://localhost:4317`     |
| `OTEL_EXPORTER_OTLP_PROTOCOL` | OTLP protocol (`grpc` or `http/protobuf`)     | `grpc`                      |
| `OTEL_EXPORTER_OTLP_INSECURE` | Disable TLS for the OTLP exporter             | `true`                      |
| `OTEL_LOGS_EXPORTER`          | Log exporter (`otlp`, `console`, `none`)      | `otlp`                      |
| `OTEL_PYTHON_LOG_CORRELATION` | Inject trace/span IDs into logs               | `true`                      |
| `OTEL_RESOURCE_ATTRIBUTES`    | Resource attributes (e.g. `service.name=...`) | `service.name=...`          |

See [.env.example](.env.example) for the full template.

---

## Observability

This starter ships with first-class OpenTelemetry support:

- **Tracing** — automatic instrumentation of FastAPI requests via `FastAPIInstrumentor`
- **Logging** — `LoggingInstrumentor` injects `trace_id` / `span_id` into every log record
- **Request logging** — custom middleware logs method, path, status, and duration with a unique request ID
- **Structured output** — JSON logs in production, colorized console output during development

Point `OTEL_EXPORTER_OTLP_ENDPOINT` at any OTLP-compatible collector (Grafana Alloy,
Jaeger, Tempo, OpenTelemetry Collector, etc.) to start exporting telemetry.

---

## Testing

```bash
# Run the full suite
make test

# With coverage (HTML + terminal report)
make test-cov

# Run a single test
uv run pytest tests/test_todos.py::test_create_todo -v
```

Tests use an isolated SQLite database and a `TestClient` fixture defined in
[tests/conftest.py](tests/conftest.py).

---

## Managing Dependencies

```bash
uv add <package>                # Add a runtime dependency
uv add --group dev <package>    # Add a development dependency
uv remove <package>             # Remove a dependency
uv lock                         # Refresh the lockfile
```

---

## Tech Stack

**Runtime**

- Python 3.12+
- FastAPI 0.115+
- SQLModel 0.0.22+
- Uvicorn (ASGI server)
- SQLite

**Tooling**

- [uv](https://docs.astral.sh/uv/) — package & environment manager
- [Ruff](https://docs.astral.sh/ruff/) — linter & formatter
- [ty](https://docs.astral.sh/ty/) — static type checker
- [pytest](https://docs.pytest.org/) — testing framework
- Docker & Docker Compose

---

## License

Released under the [MIT License](https://opensource.org/licenses/MIT).
