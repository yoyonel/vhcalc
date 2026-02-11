set shell := ["bash", "-uc"]

# Install project dependencies
install:
    cd python && uv sync --all-extras --dev

# Run tests
test:
    cd python && uv run pytest

# Lint code
lint:
    cd python && uv run ruff check .
    cd python && uv run mypy .

# Format code
format:
    cd python && uv run ruff format .
    cd python && uv run ruff check --fix .

# Build Python package
build:
    cd python && uv build

# Build Docker image
docker-build:
    cd python && docker build -t vhcalc:latest .

# Run the application (Python version)
run *args:
    cd python && uv run vhcalc {{args}}

# Show this help message
help:
    @just --list
