from datetime import datetime
from utils import cosine_distance
from config import CONFIDENCE_THRESHOLD, EMBEDDING_THRESHOLD
from PIL import Image

class Processor:
    def __init__(self, detector, analyzer):
        self.detector = detector
        self.analyzer = analyzer
        self.embeddings = {}

    def process_frame(self, frame):
        nearest_person_bbox = self.detector.detect_faces(frame, confidence = CONFIDENCE_THRESHOLD)
        today = datetime.now()
        output = False
        if nearest_person_bbox is not None:
            x1, y1, x2, y2 = map(int, nearest_person_bbox)
            cropped_face = frame[y1:y2, x1:x2]
            cropped_face_pil = Image.fromarray(cropped_face)

            # Analyze face
            age, gender = self.analyzer.get_age_gender(cropped_face_pil)
            embedding = self.analyzer.get_embedding(cropped_face_pil)

            # Match or assign visitor ID
            matched = False
            for visitor_id, stored_embedding in self.embeddings.items():
                if cosine_distance(embedding, stored_embedding) < EMBEDDING_THRESHOLD:
                    self.embeddings[visitor_id] = (stored_embedding + embedding) / 2
                    matched = True
                    output = {
                            "visitorId": visitor_id,
                            "age": age,
                            "gender": gender,
                            "locationId": "Will provide",
                            "visitDate": today.strftime("%Y-%m-%d"),
                            "visitTime": today.strftime("%H:%M:%S"),
                            "mood": "",
                            "bodyType": "",
                            "race": "",
                            "primaryClothingColor": "",
                            "secondaryClothingColor": "",
                            "inStoreCoordinates":
                            {
                                "lat": "Will provide",
                                "lng": "Will provide",
                                "x": ["Will provide"],
                                "y": ["Will provide"]
                            },
                            "eyesFocus": ""
                            }
                    break

            if not matched:
                new_id = (f"{datetime.now().strftime('%Y%m%d')}_{len(self.embeddings) + 1}") # Replace it by today
                self.embeddings[new_id] = embedding
                output ={
                        "visitorId": new_id,
                        "age": age,
                        "gender": gender,
                        "locationId": "Will provide",
                        "visitDate": today.strftime("%Y-%m-%d"),
                        "visitTime": today.strftime("%H:%M:%S"),
                        "mood": "",
                        "bodyType": "",
                        "race": "",
                        "primaryClothingColor": "",
                        "secondaryClothingColor": "",
                        "inStoreCoordinates":
                        {
                            "lat": "Will provide",
                            "lng": "Will provide",
                            "x": ["Will provide"],
                            "y": ["Will provide"]
                        },
                        "eyesFocus": ""
                        }

        return nearest_person_bbox, output