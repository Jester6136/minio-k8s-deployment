Below is a **clean, concise, end-to-end** of the **working Lakehouse setup** using your **existing external MinIO**, with **Iceberg + Nessie + Trino + Spark**, **no Bitnami**, **100% free & official images**.

---

# ✅ Final Lakehouse Solution

## Architecture

```
Spark ─┐
       ├── Iceberg → Nessie (REST catalog)
Trino ─┘              ↓
               External MinIO (S3)
```

MinIO endpoints (already running):

* S3 API: `https://api-storage.aiacademy.edu.vn      `
* Console: `https://storage.aiacademy.edu.vn      `
* Bucket: `warehouse`

---

## 1️⃣ Folder Tree

```
datalakehouse/
├── docker-compose.yml
├── spark/
│   └── spark-defaults.conf
└── trino/
    └── catalog/
        └── iceberg.properties
```

---

## 2️⃣ Docker Composervices:
```
  version: "3.9"

services:
  nessie:
    image: projectnessie/nessie:0.76.6
    container_name: nessie
    ports:
      - "19120:19120"
    volumes:
      - ./nessie-data:/data
    environment:
      NESSIE_VERSION_STORE_TYPE: ROCKSDB

  trino:
    image: trinodb/trino:479
    container_name: trino
    ports:
      - "8080:8080"
    volumes:
      - ./trino/catalog:/etc/trino/catalog
    depends_on:
      - nessie

  spark:
    image: apache/spark:4.1.1
    container_name: spark
    command: >
      /opt/spark/bin/spark-class
      org.apache.spark.deploy.master.Master
    volumes:
      - ./spark:/opt/spark/conf
    ports:
      - "7077:7077"
      - "8081:8080"
    depends_on:
      - nessie
```

---

## 3️⃣ Spark Configurspark.sql.extensions=org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions
> spark-defaults.conf
```
spark.sql.extensions=org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions

spark.sql.catalog.nessie=org.apache.iceberg.spark.SparkCatalog
spark.sql.catalog.nessie.catalog-impl=org.apache.iceberg.nessie.NessieCatalog
spark.sql.catalog.nessie.uri=http://nessie:19120/api/v1
spark.sql.catalog.nessie.ref=main
spark.sql.catalog.nessie.warehouse=s3://warehouse/
spark.sql.catalog.nessie.io-impl=org.apache.iceberg.aws.s3.S3FileIO

spark.hadoop.fs.s3a.endpoint=https://api-storage.aiacademy.edu.vn
spark.hadoop.fs.s3a.access.key=admin
spark.hadoop.fs.s3a.secret.key=4d494e494f5f524f4f545f50415353574f5244
spark.hadoop.fs.s3a.path.style.access=true
spark.hadoop.fs.s3a.connection.ssl.enabled=true
```

> iceberg.properties
```
iceberg.catalog.type=rest
iceberg.rest-catalog.uri=http://nessie:19120/api/v1

iceberg.rest-catalog.warehouse=s3://warehouse/

fs.native-s3.enabled=true
s3.endpoint=https://api-storage.aiacademy.edu.vn
s3.path-style-access=true
s3.aws-access-key=admin
s3.aws-secret-key=4d494e494f5f524f4f545f50415353574f5244
s3.region=us-east-1
```

---

## 5️⃣ Start the Stack

```bash
docker compose down -v
docker compose pull
docker compose up -d
```

---

## 6️⃣ Test the Setup

### Spark (write Iceberg)

```bash
docker exec -it spark /opt/spark/bin/spark-sql
```

```sql
CREATE TABLE nessie.demo.users (
  id INT,
  name STRING
) USING iceberg;

INSERT INTO nessie.demo.users VALUES (1, 'Alice');
```

### Trino (read Iceberg)

Open → [http://localhost:8080](http://localhost:8080)

```sql
SELECT * FROM iceberg.demo.users;
```

### MinIO

Check bucket:

```
warehouse/demo/users/
```

---