## Architecture

```
Spark ─┐
       ├── Iceberg → Nessie (REST catalog)
Trino ─┘              ↓
               External MinIO (S3)
```

MinIO endpoints (already running):

* S3 API: `https://api-storage.aiacademy.edu.vn  `
* Console: `https://storage.aiacademy.edu.vn  `
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

## 2️⃣ Docker Compose

📄 `docker-compose.yml`

```yaml
services:

  nessie:
    image: projectnessie/nessie:latest
    container_name: nessie
    ports:
      - "19120:19120"
    environment:
      NESSIE_VERSION_STORE_TYPE: INMEMORY

  trino:
    image: trinodb/trino:latest
    container_name: trino
    ports:
      - "8080:8080"
    volumes:
      - ./trino/catalog:/etc/trino/catalog
    depends_on:
      - nessie

  spark:
    image: apache/spark:3.5.0
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

## 3️⃣ Spark Configuration (Iceberg + Nessie + MinIO)

📄 `spark/spark-defaults.conf`

```properties
spark.sql.extensions=org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions

spark.jars.packages=\
org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.5.2,\
org.projectnessie:nessie-spark-extensions-3.5_2.12:0.84.0

spark.sql.catalog.nessie=org.apache.iceberg.spark.SparkCatalog
spark.sql.catalog.nessie.catalog-impl=org.apache.iceberg.nessie.NessieCatalog
spark.sql.catalog.nessie.uri=http://nessie:19120/api/v1
spark.sql.catalog.nessie.ref=main
spark.sql.catalog.nessie.warehouse=s3://warehouse/
spark.sql.catalog.nessie.io-impl=org.apache.iceberg.aws.s3.S3FileIO

spark.hadoop.fs.s3a.endpoint=https://api-storage.aiacademy.edu.vn  
spark.hadoop.fs.s3a.access.key=YOUR_ACCESS_KEY
spark.hadoop.fs.s3a.secret.key=YOUR_SECRET_KEY
spark.hadoop.fs.s3a.path.style.access=true
spark.hadoop.fs.s3a.connection.ssl.enabled=true
```

---

## 4️⃣ Trino Iceberg Catalog

📄 `trino/catalog/iceberg.properties`

```properties
connector.name=iceberg

iceberg.catalog.type=rest
iceberg.rest-catalog.uri=http://nessie:19120/api/v1
iceberg.rest-catalog.ref=main
iceberg.rest-catalog.warehouse=s3://warehouse/

fs.native-s3.enabled=true
s3.endpoint=https://api-storage.aiacademy.edu.vn  
s3.aws-access-key=YOUR_ACCESS_KEY
s3.aws-secret-key=YOUR_SECRET_KEY
s3.path-style-access=true
s3.ssl.enabled=true
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

## ✅ Key Design Decisions

* ❌ Bitnami Spark removed (commercial)
* ✅ Apache official Spark image
* ✅ External MinIO (production-grade)
* ✅ Nessie REST catalog (Git-like Iceberg)
* ✅ Iceberg shared by Spark & Trino