import cv2
import json
import time
from detection import DeepFaceDetector
from analysis import Analyzer
from processor import Processor
from config import (
    PROCESS_INTERVAL_SEC,
    TRACKING_DURATION_SEC,
    CONFIDENCE_THRESHOLD,
    MIN_FACE_RATIO,
    DEFAULT_CAMERA_INDEX
)
from utils import IDTracker
from kafka_producer import send_to_kafka


class FaceProcessor:
    def __init__(self, 
                 process_interval_sec=PROCESS_INTERVAL_SEC,
                 tracking_duration_sec=TRACKING_DURATION_SEC,
                 confidence_threshold=CONFIDENCE_THRESHOLD,
                 min_face_ratio=MIN_FACE_RATIO,
                 default_camera_index=DEFAULT_CAMERA_INDEX,
                 identify_age=False,
                 identify_gender=False,
                 output_location=False):
        # Configuration parameters from config
        self.process_interval_sec = process_interval_sec
        self.tracking_duration_sec = tracking_duration_sec
        self.confidence_threshold = confidence_threshold
        self.min_face_ratio = min_face_ratio
        self.default_camera_index = default_camera_index
        self.output_location = output_location
        self.identify_age = identify_age
        self.identify_gender = identify_gender

        # Initialize components
        self.detector = DeepFaceDetector(
            confidence=self.confidence_threshold,
            min_face_ratio=self.min_face_ratio
        )
        self.analyzer = Analyzer(
            identify_age=identify_age,  # using instance variables if needed
            identify_gender=identify_gender
        )
        self.processor = Processor(self.detector, self.analyzer)
        self.tracker = IDTracker(tracking_duration_sec=self.tracking_duration_sec)
        self.last_save_time = time.time()

        # Set up the camera
        self.cap = cv2.VideoCapture(self.default_camera_index)
        if self.cap.isOpened():
            print("Camera has opened successfully")
        else:
            print("Could not open webcam.")

    def run(self):
        if not self.cap.isOpened():
            return

        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to retrieve frame. Exiting...")
                break

            # Process the frame
            bbox_coordinate, result = self.processor.process_frame(frame)
            if result:
                current_time = time.time()
                if current_time - self.last_save_time > self.process_interval_sec:
                    # Log result in JSON Lines format
                    if self.output_location:
                        with open(self.output_location, "a") as f:
                            f.write(json.dumps(result) + "\n")
                        self.last_save_time = current_time

                # Display the results on the frame
                predicted_age = result.get("age", 0)
                predicted_gender = result.get("gender", "Neutral")
                x1, y1, x2, y2 = map(int, bbox_coordinate)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 4)

                try:
                    if predicted_age < 20:
                        predicted_age = "below 20"
                    elif predicted_age > 60:
                        predicted_age = "above 60"
                    else:
                        predicted_age = f"{predicted_age-5}-{predicted_age+5}"
                except Exception:
                    predicted_age = 0

                text = f"Age:{predicted_age} || Gender:{predicted_gender}"
                cv2.putText(frame, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX,
                            0.8, (0, 255, 0), 3, cv2.LINE_AA)

                # API call
                person_id = result["visitorId"]
                api_person_id = self.tracker.check_for_api(person_id)
                if api_person_id:
                    print(result)
                    send_to_kafka(result)

            # (Optional) Show the camera feed in a window
            cv2.imshow('Webcam Feed', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Cleanup
        self.cap.release()
        cv2.destroyAllWindows()


# if __name__ == "__main__":
#     face_processor = FaceProcessor(output_location="results.json", identify_age = False, identify_gender = True)
#     face_processor.run()