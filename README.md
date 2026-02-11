# vhcalc

This repository contains implementations of the `vhcalc` video hashing algorithm.

## Structure

*   [`python/`](python/README.md): The Python implementation (legacy/reference).
*   [`c/`](c/): The C implementation (work in progress).

## Python Version

See [python/README.md](python/README.md) for details on how to install and run the Python version using `uv`.

## C Version

(Instructions for C version will be added here)

## Development

This project uses [`just`](https://github.com/casey/just) as a command runner.

### Available commands

*   `just install`: Install project dependencies.
*   `just test`: Run the test suite.
*   `just lint`: Check code quality (Ruff, Mypy).
*   `just format`: Format code (Ruff).
*   `just build`: Build the Python package.
*   `just docker-build`: Build the Docker image.
*   `just run [args]`: Run the application (e.g., `just run --help`).
