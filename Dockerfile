FROM python:3.9-slim-bullseye

ARG USERNAME=yoyonel

ENV PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=$PATH:/home/$USERNAME/.local/bin

RUN useradd --create-home $USERNAME
USER $USERNAME
WORKDIR /home/$USERNAME

COPY . /home/$USERNAME/

RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install --no-cache-dir -r requirements.txt
