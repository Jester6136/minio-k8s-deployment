from kafka import KafkaConsumer
import json

# ⚙️ Thay đổi nếu bạn expose Kafka ra NodePort
KAFKA_BROKER = "localhost:32004"   # hoặc "kafka.kafka.svc.cluster.local:9092" nếu chạy trong cluster
TOPIC = "minio-events"

# Tạo consumer
consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=[KAFKA_BROKER],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='minio-event-listener',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

print(f"🚀 Listening for MinIO events on topic '{TOPIC}' ...")

for message in consumer:
    event = message.value
    print("📦 Received event:")
    print(json.dumps(event, indent=2))
