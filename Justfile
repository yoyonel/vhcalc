set shell := ["bash", "-uc"]

# Install project dependencies
install:
    uv sync --all-extras --dev

# Run tests
test:
    uv run pytest

# Lint code
lint:
    uv run ruff check .
    uv run mypy .

# Format code
format:
    uv run ruff format .
    uv run ruff check --fix .

# Build Python package
build:
    uv build

# Build Docker image
docker-build:
    docker build -t vhcalc:latest .

# Run the application (Python version)
run *args:
    uv run vhcalc {{args}}

# Show this help message
help:
    @just --list
