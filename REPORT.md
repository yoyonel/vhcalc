# Docker Optimization Report

## Overview
Optimized Dockerfiles for `vhcalc` using `uv` for dependency management and multi-stage builds.
Three variants provided:
- `Dockerfile` (Main): Based on `python:3.12-slim-bookworm`.
- `Dockerfile.alpine`: Based on `python:3.12-alpine`.
- `Dockerfile.distroless`: Based on `gcr.io/distroless/python3-debian12`.

## Comparison (Estimated)

| Variant | Base Image Size (Compressed) | Estimated Final Image Size (Uncompressed) | Build Time (Estimated) | Security |
| :--- | :--- | :--- | :--- | :--- |
| **Main** | ~48 MB | ~230 MB | Fast (Binary Wheels) | Good (Non-root user) |
| **Alpine** | ~18 MB | ~160 MB | Medium (Possible compilation) | Good (Non-root user, minimal OS) |
| **Distroless** | ~20 MB | ~170 MB | Fast (Copy from Main) | Best (No shell, minimal attack surface) |

*Note: Actual build times and sizes could not be verified in the current environment due to `overlayfs` mount limitations in the sandbox.*

## Key Changes
1.  **Migration to PEP 621**: `pyproject.toml` updated to standard format, replacing Poetry with `hatchling` backend.
2.  **uv Integration**: `uv` is used for fast, reliable dependency installation (`uv sync --frozen`). `uv.lock` ensures reproducible builds.
3.  **Security**: All images run as non-root user (UID 1000). Distroless image minimizes attack surface.
4.  **Optimization**: Multi-stage builds reduce final image size by excluding build tools and caches.

## Verification
- `uv sync` verified locally: Success.
- Unit tests (`pytest`): Passed.
