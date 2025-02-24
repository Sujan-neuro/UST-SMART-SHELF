from datetime import datetime
from PIL import Image
from torchvision import transforms

from utils import (cosine_distance, 
                   LimitedDict, 
                   DailyIndex
                   )
from config import (CONFIDENCE_THRESHOLD, 
                    EMBEDDING_THRESHOLD, 
                    MAX_EMBEDDING_TO_MATCH
                    )

# Image preprocessing class
class ImagePreprocessor:
    def __init__(self):
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def preprocess(self, image):
        image_tensor = self.transform(image).unsqueeze(0)  # Add batch dimension
        return image_tensor



class Processor:
    def __init__(self, detector, analyzer):
        self.detector = detector
        self.analyzer = analyzer
        self.embeddings = LimitedDict(max_size = MAX_EMBEDDING_TO_MATCH)
        self.daily_index = DailyIndex()

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
                index = self.daily_index.get_index()
                new_id = (f"{today.strftime('%Y%m%d')}_{index}")
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