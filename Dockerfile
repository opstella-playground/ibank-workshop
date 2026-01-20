# syntax=docker/dockerfile:1
# check=error=true

ARG BASE_IMAGE=registry.orion.opstella.in.th/shared/python3-with-uv:latest

# Build stage
FROM ${BASE_IMAGE} AS builder

# Install dependencies
COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev --no-install-project

# Production stage
FROM ${BASE_IMAGE} AS production

# Create non-root user for security
RUN groupadd --gid 1000 appgroup && \
    useradd --uid 1000 --gid appgroup --shell /bin/bash --create-home appuser

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY app ./app

# Create data directory for SQLite
RUN mkdir -p /app/data && chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Run the application
CMD [ \
    "uvicorn", "app.main:app", \
    "--host", "0.0.0.0", \
    "--port", "8000", \
    "--no-server-header", \
    "--proxy-headers" \
    ]
