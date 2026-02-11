FROM python:3.12-slim-bookworm AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Compile bytecode for faster startup
ENV UV_COMPILE_BYTECODE=1
# Copy instead of hardlink to avoid issues when copying .venv to final stage
ENV UV_LINK_MODE=copy

WORKDIR /app

# Install dependencies
# Using --mount to leverage cache
COPY pyproject.toml uv.lock ./
# Need README for package metadata (if referenced in pyproject.toml)
COPY docs/README.md ./docs/README.md
# Need source code to install the project
COPY vhcalc ./vhcalc

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable

FROM python:3.12-slim-bookworm

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends libmediainfo0v5 && \
    rm -rf /var/lib/apt/lists/*

# Create user
RUN useradd -m -u 1000 vhcalc

USER vhcalc
WORKDIR /app

# Copy venv from builder
COPY --from=builder --chown=vhcalc:vhcalc /app/.venv /app/.venv

# Add venv to PATH
ENV PATH="/app/.venv/bin:$PATH"

# Entrypoint
ENTRYPOINT ["vhcalc"]
CMD ["-", "-"]
