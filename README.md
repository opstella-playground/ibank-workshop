# FastAPI Todo Starter Kit

A production-ready FastAPI starter kit with a sample Todo CRUD API, SQLite database, and Docker support. Built with modern Python tooling from [Astral](https://astral.sh/).

## Features

- 🚀 **FastAPI** - Modern, fast Python web framework
- 📦 **SQLModel** - SQL databases with Pydantic models
- 🗄️ **SQLite** - Lightweight, file-based database
- 🐳 **Docker** - Containerized for development and production
- ✅ **Testing** - Pytest with test fixtures
- 🔧 **Configuration** - Environment-based settings with Pydantic
- 📚 **API Documentation** - Auto-generated OpenAPI/Swagger docs

### Astral Tooling ✨

- ⚡ **[uv](https://docs.astral.sh/uv/)** - Blazingly fast Python package manager (10-100x faster than pip)
- 🔍 **[Ruff](https://docs.astral.sh/ruff/)** - Extremely fast Python linter & formatter
- 🔬 **[ty](https://docs.astral.sh/ty/)** - Fast Python type checker

## Project Structure

```
fastapi/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI application
│   ├── config.py         # Configuration settings
│   ├── database.py       # Database setup
│   ├── models/
│   │   ├── __init__.py
│   │   └── todo.py       # Todo models
│   └── routers/
│       ├── __init__.py
│       └── todos.py      # Todo API routes
├── tests/
│   ├── __init__.py
│   ├── conftest.py       # Test fixtures
│   └── test_todos.py     # Todo API tests
├── data/                 # SQLite database (gitignored)
├── Dockerfile            # Production Dockerfile
├── Dockerfile.dev        # Development Dockerfile
├── docker-compose.yml    # Production compose
├── docker-compose.dev.yml # Development compose
├── pyproject.toml        # Project configuration
├── uv.lock               # Lockfile for reproducible installs
├── Makefile              # Convenient development commands
├── .env.example          # Environment template
└── README.md
```

## Quick Start

### Prerequisites

Install **uv** (ultra-fast Python package manager):

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or with Homebrew
brew install uv
```

### Local Development

1. **Clone and install dependencies:**
   ```bash
   cd fastapi
   uv sync --all-groups
   ```

2. **Copy environment file:**
   ```bash
   cp .env.example .env
   ```

3. **Run the development server:**
   ```bash
   uv run fastapi dev app/main.py
   # Or use make:
   make dev
   ```

4. **Open the API docs:**
   - Swagger UI: http://127.0.0.1:8000/docs
   - ReDoc: http://127.0.0.1:8000/redoc

### Using Make Commands

```bash
make help        # Show all available commands
make install     # Install dependencies
make dev         # Run dev server with hot-reload
make test        # Run tests
make check       # Run all linters (lint + format + typecheck)
```

### Docker Development

```bash
# Build and run with hot-reload
make docker-dev
# Or directly:
docker compose -f docker-compose.dev.yml up --build
```

### Docker Production

```bash
# Build and run production image
make docker-prod
# Or directly:
docker compose up --build -d

# Check health
docker compose ps
```

## Code Quality

### Linting with Ruff

```bash
# Check for issues
uv run ruff check app tests

# Fix auto-fixable issues
uv run ruff check app tests --fix

# Or use make:
make lint
make lint-fix
```

### Formatting with Ruff

```bash
# Format code
uv run ruff format app tests

# Check formatting without changes
uv run ruff format app tests --check

# Or use make:
make format
```

### Type Checking with ty

```bash
# Run type checker
uv run ty check app

# Or use make:
make typecheck
```

### Run All Checks

```bash
make check  # Runs lint-fix, format, and typecheck
```

## API Endpoints

### Todos CRUD

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/todos/` | List all todos |
| `POST` | `/api/v1/todos/` | Create a new todo |
| `GET` | `/api/v1/todos/{id}` | Get a specific todo |
| `PATCH` | `/api/v1/todos/{id}` | Update a todo |
| `DELETE` | `/api/v1/todos/{id}` | Delete a todo |

### Query Parameters

- `offset` - Number of items to skip (default: 0)
- `limit` - Max items to return (default: 20, max: 100)
- `completed` - Filter by completion status (true/false)

### Example Requests

**Create a Todo:**
```bash
curl -X POST "http://localhost:8000/api/v1/todos/" \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries", "description": "Milk, eggs, bread", "priority": 3}'
```

**List Todos:**
```bash
curl "http://localhost:8000/api/v1/todos/?limit=10&completed=false"
```

**Update a Todo:**
```bash
curl -X PATCH "http://localhost:8000/api/v1/todos/1" \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'
```

**Delete a Todo:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/todos/1"
```

## Testing

```bash
# Run all tests
uv run pytest
# Or:
make test

# Run with coverage
uv run pytest --cov=app --cov-report=term-missing
# Or:
make test-cov

# Run specific test
uv run pytest tests/test_todos.py::test_create_todo -v
```

## Configuration

Environment variables (see `.env.example`):

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_NAME` | Application name | FastAPI Todo Starter |
| `APP_VERSION` | Application version | 0.1.0 |
| `DEBUG` | Enable debug mode | false |
| `DATABASE_URL` | SQLite database path | sqlite:///./data/todos.db |
| `API_PREFIX` | API route prefix | /api/v1 |

## Adding Dependencies

```bash
# Add a production dependency
uv add <package>

# Add a dev dependency
uv add --group dev <package>

# Remove a dependency
uv remove <package>
```

## Tech Stack

- **Python** 3.12 LTS
- **FastAPI** 0.115+
- **SQLModel** 0.0.22+
- **SQLite** (built-in)
- **Uvicorn** ASGI server

### Development Tools

- **[uv](https://docs.astral.sh/uv/)** - Package manager
- **[Ruff](https://docs.astral.sh/ruff/)** - Linter & Formatter
- **[ty](https://docs.astral.sh/ty/)** - Type checker
- **Pytest** - Testing framework
- **Docker** & Docker Compose

## License

MIT License
