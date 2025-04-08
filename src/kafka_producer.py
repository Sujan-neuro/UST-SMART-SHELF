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

# result = {'visitorId': '20250304_21', 
#           'age': 41, 
#           'gender': 'Male', 
#           'locationId': '65e054c3368caa35f73ad2b4', 
#           'visitDate': '2025-03-05', 
#           'visitTime': '11:52:44', 
#           'mood': '', 'bodyType': '', 'race': '', 'primaryClothingColor': '', 'secondaryClothingColor': '', 'inStoreCoordinates': {'lat': '1.2897', 'lng': '103.8501', 'x': [''], 'y': ['']}, 'eyesFocus': '', 'type': 'store'}
# send_to_kafka(result, topics = ['lenovo_event'])