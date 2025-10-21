from kafka import KafkaProducer

# Thay IP bên dưới bằng IP node của bạn
producer = KafkaProducer(bootstrap_servers='14.224.231.82:32004')

# Gửi thử một message
producer.send('test-topic', b'Hello from Python!')
producer.flush()
print("✅ Message sent!")
