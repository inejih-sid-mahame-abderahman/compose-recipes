# ML for CyberSecurity Lab Environment

This directory provides a containerized Python lab environment for practical work involving:

- data analysis and machine learning;
- applied cryptography experiments;
- secure data processing;
- privacy and adversarial ML testing;

The environment is designed to be reproducible and easy to start on a standard CPU-only machine.

## Main components

The lab includes:

- JupyterLab
- Python scientific stack
- scikit-learn
- PyTorch (CPU only)
- FastAPI
- SQLite and DuckDB
- cryptographic libraries and CLI tools
- privacy and adversarial ML libraries

## Services and ports

- JupyterLab: `http://localhost:8888`
- API testing port: `http://localhost:8000`

Default Jupyter token:

```text
mlsec-lab
````

## Project layout

```text
.
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── datasets/
└── workspace/
    ├── notebooks/
    ├── data/
    ├── models/
    ├── reports/
    ├── exports/
    ├── db/
    └── apps/
```

## Start the environment

Build and start the container:

```bash
docker compose up --build -d
```

Check that the service is running:

```bash
docker compose ps
```

View recent logs:

```bash
docker compose logs -n 50
```

## Stop the environment

```bash
docker compose down
```

## Open a shell in the container

```bash
docker compose exec mlsec-lab bash
```

## Storage and paths

Inside the container:

* `/workspace/notebooks` : notebooks
* `/workspace/data` : working datasets
* `/workspace/models` : saved models
* `/workspace/reports` : reports and notes
* `/workspace/apps` : API code
* `/workspace/db/lab.db` : SQLite database
* `/datasets` : mounted read-only datasets

## Quick validation

After startup, open JupyterLab in your browser and log in with the token above.

Then run the smoke test below from your host machine.

## Smoke test script

Save the following as `test_env.sh` at the root of the project:

```bash
#!/usr/bin/env bash
set -euo pipefail

echo "[1/7] Checking container status..."
docker compose ps

echo "[2/7] Checking runtime user and core tools..."
docker compose exec mlsec-lab bash -lc '
whoami
id
python --version
pip --version
openssl version
gpg --version
sqlite3 --version
'

echo "[3/7] Testing Python imports..."
docker compose exec mlsec-lab python - <<'PY'
import pandas
import numpy
import sklearn
import matplotlib
import cryptography
import sqlalchemy
import fastapi
import uvicorn
import duckdb
import torch
import opacus
import diffprivlib
import art
import foolbox
print("All key imports succeeded.")
PY

echo "[4/7] Checking PyTorch CPU mode..."
docker compose exec mlsec-lab python - <<'PY'
import torch
print("torch version:", torch.__version__)
print("cuda available:", torch.cuda.is_available())
print("device count:", torch.cuda.device_count())
assert torch.cuda.is_available() is False
print("CPU-only check passed.")
PY

echo "[5/7] Testing SQLite write access..."
docker compose exec mlsec-lab python - <<'PY'
import sqlite3
conn = sqlite3.connect("/workspace/db/lab.db")
conn.execute("CREATE TABLE IF NOT EXISTS smoke_test (id INTEGER PRIMARY KEY, value TEXT)")
conn.execute("INSERT INTO smoke_test(value) VALUES (?)", ("ok",))
conn.commit()
rows = conn.execute("SELECT COUNT(*) FROM smoke_test").fetchone()[0]
conn.close()
print("SQLite OK, rows =", rows)
PY

echo "[6/7] Testing cryptography..."
docker compose exec mlsec-lab python - <<'PY'
from cryptography.fernet import Fernet
key = Fernet.generate_key()
f = Fernet(key)
ciphertext = f.encrypt(b"hello")
plaintext = f.decrypt(ciphertext)
assert plaintext == b"hello"
print("Cryptography OK")
PY

echo "[7/7] Testing a basic ML workflow..."
docker compose exec mlsec-lab python - <<'PY'
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)
clf = RandomForestClassifier(random_state=42)
clf.fit(X_train, y_train)
score = clf.score(X_test, y_test)
print("ML workflow OK, accuracy =", score)
PY

echo "Environment smoke test passed."
```

Make it executable:

```bash
chmod +x test_env.sh
```

Run it:

```bash
./test_env.sh
```

## Optional API test

Create a simple FastAPI app in `workspace/apps/test_api.py`:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}
```

Run it inside the container:

```bash
docker compose exec mlsec-lab bash -lc 'uvicorn apps.test_api:app --host 0.0.0.0 --port 8000'
```

In another terminal, test it:

```bash
curl http://localhost:8000/health
```

Expected result:

```json
{"status":"ok"}
```

## Notes

* The environment is intended for CPU-only usage.
* Datasets are mounted read-only by default.
* The SQLite database file is stored in `./workspace/db/lab.db`.
* Persisted work remains in the local `workspace/` directory.
