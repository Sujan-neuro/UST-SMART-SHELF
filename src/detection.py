from ultralytics import YOLO
    
class Detector:
    def __init__(self, model_path):
        self.model = YOLO(model_path)
        self.previous_person_id = None  # To track the currently identified person

    def detect_faces(self, frame, confidence = 0.8):
        """
        Detect faces using YOLO.
        """
        results = self.model.predict(source = frame, conf = confidence, verbose = False)
        boxes, max_area, nearest_person_bbox = [], 0, None

        for result in results:
            for bbox, conf, cls_id in zip(result.boxes.xyxy, result.boxes.conf, result.boxes.cls):
                if cls_id == 0 and conf > confidence:  # Class ID 0 for person
                    bbox_np = bbox.cpu().numpy()
                    boxes.append(bbox_np)

                    # Calculate the area of the bounding box
                    area = (bbox_np[2] - bbox_np[0]) * (bbox_np[3] - bbox_np[1])
                    if area > max_area:  # Identify the nearest person based on the largest bounding box
                        max_area = area
                        nearest_person_bbox = bbox_np

        # If no person is detected, return empty lists
        return nearest_person_bbox