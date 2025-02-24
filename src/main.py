import cv2, json, time
from detection import DeepFaceDetector
from analysis import Analyzer
from processor import Processor
from config import PROCESS_INTERVAL_SEC , TRACKING_DURATION_SEC
from utils import IDTracker
from kafka_producer import send_to_kafka


def main(output_location):
    detector = DeepFaceDetector () ## Added newly
    analyzer = Analyzer()
    processor = Processor(detector, analyzer)
    tracker = IDTracker(tracking_duration_sec = TRACKING_DURATION_SEC)
    last_save_time = time.time()

    # Capture from the default webcam (use index 0 or higher if you have multiple cameras)
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        print("Camera has opened successfully")
    if not cap.isOpened():
        print("Could not open webcam.")
        return
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to retrieve frame. Exiting...")
            break
        
        # Process the frame
        bbox_coordinate, result = processor.process_frame(frame)
        if result:
            current_time = time.time()
            if current_time - last_save_time > PROCESS_INTERVAL_SEC:
                # Log result to the file in JSON Lines format only
                with open(output_location, "a") as f:
                    f.write(json.dumps(result) + "\n")
                last_save_time = current_time

            # Show the features on the display for each frame
            predicted_age = result.get("age", "Unknown")
            predicted_gender = result.get("gender", "Unknown")
            x1, y1, x2, y2 = map(int, bbox_coordinate)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 4)
            text = f"Age:{predicted_age} || Gender:{predicted_gender}"  # Sample label
            cv2.putText(frame, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 3, cv2.LINE_AA)

            # API call
            person_id = result["visitorId"]
            api_person_id = tracker.check_for_api(person_id)
            if api_person_id:
                print(result)
                send_to_kafka(result)
        # (Optional) Show the camera feed in a window
        cv2.imshow('Webcam Feed', frame)
        # Press 'q' to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main("results.json")