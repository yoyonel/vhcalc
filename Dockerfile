FROM python:3.13.0b4-slim as builder

ARG USERNAME=yoyonel

ENV PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=$PATH:/home/$USERNAME/.local/bin

RUN useradd --create-home $USERNAME
USER $USERNAME
WORKDIR /home/$USERNAME

COPY . /home/$USERNAME/

RUN echo '***VERSION python in builder image' && \
    python --version

# hadolint ignore=DL3013
RUN rm -rf ~/.cache/pip && \
    python -m pip cache purge && \
    python3 -m pip install --no-cache-dir --upgrade pip && \
    python3 -m pip install --no-cache-dir -r requirements.txt && \
    pip wheel -w wheels --no-deps -e .


FROM python:3.13.0b4-slim

ARG USERNAME=yoyonel

ENV PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=$PATH:/home/$USERNAME/.local/bin

RUN useradd --create-home $USERNAME
USER $USERNAME
WORKDIR /home/$USERNAME

RUN echo '***VERSION python in final image' && \
    python --version

COPY --from=builder /home/$USERNAME/wheels /home/$USERNAME/wheels

ENV PIP_NO_CACHE_DIR=1
# hadolint ignore=DL3013
RUN set -ex && \
    \
    python -m pip install --upgrade pip && \
    PIP_FIND_LINKS="/home/$USERNAME/wheels" pip install /home/$USERNAME/wheels/vhcalc* && \
    rm -rf /home/$USERNAME/.cache

ENTRYPOINT ["vhcalc"]
CMD ["--version"]
