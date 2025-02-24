from deepface import DeepFace

# Detect faces using Deepface    
class DeepFaceDetector:
        """
        Detects and extracts faces using DeepFace.
        Returns the bounding box (x1, y1, x2, y2) of the face with highest confidence.
        """

        def detect_faces(self, frame, confidence = 0.5):
            try:
                detected_faces = DeepFace.extract_faces(frame, detector_backend="opencv")  # You can use mtcnn, dlib, etc.
                if not detected_faces:
                    return None  # No faces detected
                
                # Filter faces by confidence level
                valid_faces = [face for face in detected_faces if face.get("confidence", 0) >= confidence]

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

                return x1, y1, x2, y2
            except Exception as e:
                return None