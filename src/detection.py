from deepface import DeepFace

# Detect faces using DeepFace    
class DeepFaceDetector:
    """
    Detects and extracts faces using DeepFace.
    Returns the bounding box (x1, y1, x2, y2) of the face with highest confidence,
    only if the detected face area is at least 10% of the frame.
    """
    def __init__(self, confidence=0.5, min_face_ratio=0.1):
        self.confidence = confidence
        self.min_face_ratio = min_face_ratio
    
    def detect_faces(self, frame):
        try:
            frame_height, frame_width = frame.shape[:2]  # Get frame dimensions
            frame_area = frame_width * frame_height  # Calculate total frame area
            
            detected_faces = DeepFace.extract_faces(frame, detector_backend="opencv")
            if not detected_faces:
                return None  # No faces detected
            
            # Filter faces by confidence level
            valid_faces = [face for face in detected_faces if face.get("confidence", 0) >= self.confidence]
            
            if not valid_faces:
                return None  # No faces meet the confidence threshold
            
            # Select the largest face (assumed nearest) among valid faces
            nearest_face = max(valid_faces, key=lambda x: x["facial_area"]["w"] * x["facial_area"]["h"])
            
            # Get bounding box coordinates
            x1 = nearest_face["facial_area"]["x"]
            y1 = nearest_face["facial_area"]["y"]
            width = nearest_face["facial_area"]["w"]
            height = nearest_face["facial_area"]["h"]
            x2 = x1 + width
            y2 = y1 + height
            
            # Calculate detected face area
            face_area = width * height
            
            # Check if face area is at least the minimum required percentage of frame area
            if face_area / frame_area < self.min_face_ratio:
                return None  # Face is too small
            
            return x1, y1, x2, y2
        except Exception as e:
            return None
