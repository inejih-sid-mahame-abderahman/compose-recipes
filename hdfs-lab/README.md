# Hadoop + HDFS + Hive (Single Node) — Docker Compose

This repository provides a **single-node Hadoop (HDFS + YARN) + Hive (Metastore + HiveServer2)** environment using Docker Compose.

It runs:
- **1 container** for Hadoop + Hive services
- **1 container** for PostgreSQL (Hive Metastore DB)

A host folder can be mounted as `./data:/data` so you can easily load files into Hive (`LOAD DATA LOCAL INPATH`) and upload files to HDFS.

---

## Services

### `hadoop-hive-single` (Hadoop + Hive)
Runs:
- HDFS (NameNode + DataNode)
- YARN (ResourceManager + NodeManager)
- Hive Metastore (Thrift on `9083`)
- HiveServer2 (JDBC on `10000`)
- SSHD (needed for Hadoop `start-dfs.sh` scripts)

### `hive-metastore-db` (PostgreSQL)
Stores Hive metastore schema and metadata.

---

## Ports (host → container)

| Service | Port | URL / Usage |
|---|---:|---|
| NameNode UI | 9870 | `http://localhost:9870` |
| YARN ResourceManager UI | 8088 | `http://localhost:8088` |
| HDFS RPC | 9000 | `hdfs://localhost:9000` |
| HiveServer2 | 10000 | `jdbc:hive2://localhost:10000` |
| Hive Metastore Thrift | 9083 | `thrift://localhost:9083` |
| Postgres Metastore DB | 5432 | `localhost:5432` |

---

## Data Persistence

Docker volumes are used to persist:
- HDFS NameNode metadata
- HDFS DataNode blocks
- Hadoop temp directory
- PostgreSQL metastore database

Mounted host folder:
- `./data` on your host is visible as `/data` inside the Hadoop/Hive container.

Example mapping (in `docker-compose.yml`):
```yaml
volumes:
  - ./data:/data
````

---

## Build & Start

From the project root:

```bash
docker compose up -d --build
```

Follow logs:

```bash
docker logs -f hadoop-hive-single
```

Stop everything:

```bash
docker compose down
```

Remove volumes (⚠️ deletes HDFS + metastore DB data):

```bash
docker compose down -v
```

---

## Quick Health Checks (Host Side)

### 1) Check containers are running

```bash
docker compose ps
```

You should see both services as `Up`.

### 2) Check UIs respond

```bash
curl -I http://localhost:9870 | head -n 1
curl -I http://localhost:8088 | head -n 1
```

Expected: `HTTP/1.1 200` or `HTTP/1.1 302`.

---

## Functional Validation (Inside Container)

### 1) Verify Java + Hadoop CLI

```bash
docker exec -it hadoop-hive-single echo "$JAVA_HOME"
docker exec -it hadoop-hive-single hdfs version
docker exec -it hadoop-hive-single hadoop version
```

Expected: Hadoop version info prints without error.

### 2) Verify HDFS is up

```bash
docker exec -it hadoop-hive-single hdfs dfs -ls /
```

Expected: directory listing (may be empty aside from system dirs).

### 3) Create a test directory in HDFS

```bash
docker exec -it hadoop-hive-single bash -lc "su - hdoop -c 'hdfs dfs -mkdir -p /tp && hdfs dfs -chmod -R 1777 /tp && hdfs dfs -ls -d /tp'"
docker exec -it hadoop-hive-single bash -lc "su - hdoop -c 'hdfs dfs -mkdir -p /tp/tests'"
docker exec -it hadoop-hive-single bash -lc "su - hdoop -c 'hdfs dfs -put -f /etc/hosts /tp/tests/hosts.txt'"
docker exec -it hadoop-hive-single hdfs dfs -ls /tp/tests
docker exec -it hadoop-hive-single hdfs dfs -cat /tp/tests/hosts.txt | head
```

### 4) Verify YARN is up

```bash
docker exec -it hadoop-hive-single bash -lc "su - hdoop -c 'yarn node -list'"
```

Expected: 1 NodeManager listed (in single node mode).

---

## Hive Tests

### 1) Connect to HiveServer2 using Beeline

Inside the container:

```bash
docker exec -it hadoop-hive-single bash -lc "su - hdoop -c 'beeline -n hdoop -u jdbc:hive2://localhost:10000'"

docker exec -it hadoop-hive-single beeline -n hdoop -u jdbc:hive2://localhost:10000
```

If it connects, you’ll see a `beeline>` prompt.

### 2) Run basic SQL checks

At the `beeline>` prompt:

```sql
!set outputformat table;
SHOW DATABASES;
CREATE DATABASE IF NOT EXISTS sanity;
USE sanity;

DROP TABLE IF EXISTS t1;
CREATE TABLE t1(id INT, name STRING) STORED AS TEXTFILE;

INSERT INTO t1 VALUES (1,'alice'),(2,'bob');
SELECT * FROM t1;
```

Expected: `alice` and `bob` returned.

---

## Test Loading Data from Mounted `./data:/data`

### 1) Create a sample CSV on the host

From your host terminal:

```bash
mkdir -p ./data
cat > ./data/employees.csv << 'EOF'
1,Alice,HR,60000
2,Bob,Engineering,80000
3,Charlie,HR,70000
EOF
```

### 2) Load it in Hive (LOCAL INPATH)

Inside `beeline`:

```sql
USE sanity;

DROP TABLE IF EXISTS employees;
CREATE TABLE employees(
  id INT,
  name STRING,
  dept STRING,
  salary INT
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE;

LOAD DATA LOCAL INPATH '/data/employees.csv' INTO TABLE employees;

SELECT dept, AVG(salary) AS avg_salary
FROM employees
GROUP BY dept;
```

Expected: averages per department.

---

## Troubleshooting

### Container keeps restarting / crash-loop

Check logs:

```bash
docker logs --tail=200 hadoop-hive-single
```

### Reset everything

If HDFS formatting/metastore init got into a bad state:

```bash
docker compose down -v
docker compose up -d --build
```

---

## Useful Commands

Show Hadoop processes (inside container):

```bash
jps
```

HDFS status:

```bash
hdfs dfsadmin -report
```

Hive logs:

```bash
tail -n 200 /opt/hive/logs/metastore.out
tail -n 200 /opt/hive/logs/hiveserver2.out
```

---

## Expected “Good” State Summary

You know the environment is properly running when:

* `http://localhost:9870` loads the NameNode UI
* `http://localhost:8088` loads the YARN UI
* `hdfs dfs -ls /` works inside container
* `beeline -u jdbc:hive2://localhost:10000` connects
* Hive can `LOAD DATA LOCAL INPATH '/data/...'` successfully

---

