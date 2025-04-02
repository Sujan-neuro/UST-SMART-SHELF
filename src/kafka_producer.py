import json
from kafka import KafkaProducer
from config import TOPICS
 
# Create a producer with JSON serializer
producer = KafkaProducer(
    bootstrap_servers='139.5.190.16:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Sending JSON data to Kafka
def send_to_kafka(data, topics = TOPICS):
    for topic in  topics:
        producer.send(topic, value=data)
        print(f"Produced data to topic: {topic}")
    producer.flush()