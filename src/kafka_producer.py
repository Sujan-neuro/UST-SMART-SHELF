import json
from kafka import KafkaProducer
from config import BOOTSTRAP_SERVERS
 
# Create a producer with JSON serializer
producer = KafkaProducer(
    bootstrap_servers=BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Sending JSON data to Kafka
def send_to_kafka(data, topics_list):
    for topic in  topics_list:
        producer.send(topic, value=data)
        print(f"Produced data to topic: {topic}")
    producer.flush()