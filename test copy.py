from kafka import KafkaConsumer
import json

# Replace the IP below with your node's IP
consumer = KafkaConsumer(
    'minio-events', # The topic to consume from
    bootstrap_servers='14.224.231.82:32004',
    # Optional: Specify how to deserialize messages (value_deserializer)
    # value_deserializer=lambda m: json.loads(m.decode('utf-8')), # Use if messages are JSON
    # Optional: Specify how to deserialize keys (key_deserializer)
    # key_deserializer=lambda k: k.decode('utf-8') if k else None,
    auto_offset_reset='earliest', # Start from the beginning if no committed offset exists
    enable_auto_commit=True,      # Automatically commit offsets (default)
    group_id='test-minio-events-consume' # Consumer group ID
)

print("Consumer started, waiting for messages... (Press Ctrl+C to stop)")

try:
    for message in consumer:
        # message.value is the raw message content (bytes)
        print(f"Received message: {message.value.decode('utf-8')} from topic '{message.topic}', partition {message.partition}, offset {message.offset}")
        # Optional: Print key if your messages have one
        # print(f"Key: {message.key}")
except KeyboardInterrupt:
    print("\nStopping consumer...")
finally:
    consumer.close()
    print("Consumer closed.")