FROM debian:bookworm-slim

ARG USERNAME=student
ARG USER_UID=1000
ARG USER_GID=1000

ENV DEBIAN_FRONTEND=noninteractive \
    RUSTUP_HOME=/opt/rust/rustup \
    CARGO_HOME=/opt/rust/cargo \
    PATH=/opt/rust/cargo/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    git \
    build-essential \
    pkg-config \
    libssl-dev \
    clang \
    lld \
    cmake \
    gdb \
    ripgrep \
    hyperfine \
    jq \
    bash-completion \
    tini \
    less \
    nano \
    vim \
    python3 \
 && rm -rf /var/lib/apt/lists/*

 RUN mkdir -p "${RUSTUP_HOME}" "${CARGO_HOME}" \
 && curl -sSf https://sh.rustup.rs | sh -s -- -y --no-modify-path --default-toolchain stable \
 && rustup component add clippy rustfmt \
 && rustup target add x86_64-unknown-linux-gnu \
 && cargo install cargo-audit cargo-deny

RUN groupadd --gid "${USER_GID}" "${USERNAME}" \
 && useradd --uid "${USER_UID}" --gid "${USER_GID}" -m "${USERNAME}" -s /bin/bash \
 && mkdir -p /workspace \
 && chown -R "${USERNAME}:${USERNAME}" /workspace "${RUSTUP_HOME}" "${CARGO_HOME}"

WORKDIR /workspace
USER ${USERNAME}

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["bash", "-lc", "sleep infinity"]