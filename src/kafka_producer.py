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

TEST_PENANG = False
if TEST_PENANG:
    result = {'visitorId': '20250304_111', 
            'age': 20, 
            'gender': 'Female', 
            'locationId': '65e054c3368caa35f73ad2b4', 
            'visitDate': '2025-03-05', 
            'visitTime': '11:52:44', 
            'mood': '', 'bodyType': '', 'race': '', 'primaryClothingColor': '', 'secondaryClothingColor': '', 'inStoreCoordinates': {'lat': '1.2897', 'lng': '103.8501', 'x': [''], 'y': ['']}, 'eyesFocus': '', 'type': 'store'}
    print(result)
    topic = 'lenovo_event'
    send_to_kafka(result, topics = [topic])
    #https://player.footprints-ai.com/?code=1930287630 

TEST_AWS = False
if TEST_AWS:
    result = {'visitorId': '20250304_101', 
            'age': 21, 
            'gender': 'Male', 
            'locationId': '67e26a2b29853b7303244dc3', 
            'visitDate': '2025-03-05', 
            'visitTime': '11:52:44', 
            'mood': '', 'bodyType': '', 'race': '', 'primaryClothingColor': '', 'secondaryClothingColor': '', 'inStoreCoordinates': {'lat': '1.2897', 'lng': '103.8501', 'x': [''], 'y': ['']}, 'eyesFocus': '', 'type': 'store'}

    topic = "aws_lab_no_detection" #aws_lab_default
    print(result)
    send_to_kafka(result, topics=[topic])
    # https://player-ust.footprints-ai.com/?code=0000001234