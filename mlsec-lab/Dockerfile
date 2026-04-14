FROM jupyter/scipy-notebook:python-3.11

USER root

RUN apt-get update && apt-get install -y --no-install-recommends \
    openssl \
    gnupg \
    sqlite3 \
    curl \
    jq \
    git \
    vim \
    less \
    tree \
    zip \
    unzip \
    ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt

RUN python -m pip install --no-cache-dir --upgrade pip setuptools wheel && \
    python -m pip install --no-cache-dir -r /tmp/requirements.txt

RUN mkdir -p /workspace /datasets && \
    chown -R ${NB_UID}:${NB_GID} /workspace /datasets /home/${NB_USER}

WORKDIR /workspace

USER ${NB_UID}