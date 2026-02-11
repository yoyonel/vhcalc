FROM python:3.12-slim-bookworm AS builder

ARG USERNAME=yoyonel

ENV PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=$PATH:/home/$USERNAME/.local/bin

RUN useradd --create-home $USERNAME
USER $USERNAME
WORKDIR /home/$USERNAME

COPY --chown=$USERNAME:$USERNAME . /home/$USERNAME/

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Build wheel
RUN uv build

FROM python:3.12-slim-bookworm

ARG USERNAME=yoyonel

ENV PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=$PATH:/home/$USERNAME/.local/bin

RUN useradd --create-home $USERNAME
USER $USERNAME
WORKDIR /home/$USERNAME

COPY --from=builder /home/$USERNAME/dist /home/$USERNAME/dist

ENV PIP_NO_CACHE_DIR=1
RUN set -ex && \
    python -m pip install --upgrade pip && \
    pip install /home/$USERNAME/dist/*.whl && \
    rm -rf /home/$USERNAME/.cache

ENTRYPOINT ["vhcalc"]
# by default: expected stdin stream input and exporting result to stdout
CMD ["-", "-"]
