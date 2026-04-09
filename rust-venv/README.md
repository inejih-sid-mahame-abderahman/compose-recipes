# Rust Labs Environment

This directory provides a reproducible development environment for the Rust.

It is designed for:
- practical Rust programming;
- beginner-friendly setup for students;
- use with Docker Compose;
- use with local VS Code through Dev Containers;

The environment is based on a lightweight Debian image and includes the Rust tooling recommended for the module:
- rustup
- cargo
- clippy
- rustfmt
- cargo-audit
- cargo-deny

Additional utilities are also included to support the tutorials and labs:
- git
- gdb
- ripgrep
- hyperfine
- jq
- python3

---

## Directory structure

```text
.
├── Dockerfile
├── docker-compose.yml
├── README.md
├── .devcontainer
│   └── devcontainer.json
└── workspace
````

The `workspace/` directory is shared between the host and the container. All code should be created inside this directory.

---

## 1. Prerequisites

To use this environment with Docker Compose, install:

* Docker Engine
* Docker Compose plugin
* VS Code (optional, for Dev Container usage)

---

## 2. Start the environment with Docker Compose

Create the shared workspace directory if it does not already exist:

```bash
mkdir -p workspace
```

Build and start the environment:

```bash
docker compose up -d --build
```

Open a shell inside the container:

```bash
docker compose exec rustlab bash
```

Check the toolchain:

```bash
rustc --version
cargo --version
cargo fmt --version
cargo clippy --version
cargo audit --version
cargo deny --version
```

Stop the environment:

```bash
docker compose down
```

Stop and remove volumes:

```bash
docker compose down -v
```

---

## 3. Using the shared workspace

The local directory:

```text
./workspace
```

is mounted in the container as:

```text
/workspace
```

Example:

```bash
cd /workspace
cargo new hello_rust
cd hello_rust
cargo run
```

Any file created in `/workspace` inside the container will also be visible on the host in `./workspace`.

---

## 4. Use with VS Code Dev Containers

This environment is ready to be used with the Dev Containers extension in VS Code.

### Step 1 — Install the VS Code extensions

Install in VS Code:

* Dev Containers
* rust-analyzer

### Step 2 — Open the folder in VS Code

Open the directory root folder in VS Code.

### Step 3 — Reopen in container

Press `Ctrl+Shift+P`, then run:

```text
Dev Containers: Reopen in Container
```

VS Code will:

* start the `rustlab` service from `docker-compose.yml`;
* attach to the container;
* open `/workspace` as the working directory;
* install the recommended extensions inside the container context.

### Step 4 — Create and run a Rust project

Inside the VS Code terminal:

```bash
cargo new demo_project
cd demo_project
cargo run
```

---

## 5. Using local VS Code with the container already running

You can also start Docker Compose manually:

```bash
docker compose up -d --build
```

Then in VS Code:

1. Open the command palette.
2. Run `Dev Containers: Attach to Running Container...`
3. Select `rust-labs`

This is useful if the environment is already running and you want to attach to it directly.

---
