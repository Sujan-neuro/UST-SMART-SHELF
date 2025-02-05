import cv2, json
from detection import Detector
from analysis import Analyzer
from processor import Processor
from config import PROCESS_INTERVAL_SEC, PEOPLE_DETECTOR 
from utils import IDTracker


def main(output_location):
    detector = Detector(PEOPLE_DETECTOR)
    analyzer = Analyzer()
    processor = Processor(detector, analyzer)
    tracker = IDTracker()

    # Capture from the default webcam (use index 0 or higher if you have multiple cameras)
    cap = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)
    if cap.isOpened():
        print("Camera has opened successfully")
    if not cap.isOpened():
        print("Could not open webcam.")
        return
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    # Fallback if camera FPS cannot be determined
    if fps == 0:
        fps = 30  # or any other default value
    frame_no = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to retrieve frame. Exiting...")
            break
        # Only process frames every PROCESS_INTERVAL_SEC based on FPS
        if frame_no % int(PROCESS_INTERVAL_SEC * fps) == 0:
            bbox_coordinate, result = processor.process_frame(frame)
            if result:
                # Log result immediately to the file in JSON Lines format
                with open(output_location, "a") as f:
                    f.write(json.dumps(result) + "\n")

                predicted_age = result.get("age", "Unknown")
                predicted_gender = result.get("gender", "Unknown")

                x1, y1, x2, y2 = map(int, bbox_coordinate)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 4)

                text = f"Age:{predicted_age} || Gender:{predicted_gender}"  # Sample label
                cv2.putText(frame, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 3, cv2.LINE_AA)

                person_id = result["visitorId"]
                api_person_id = tracker.check_for_api(person_id)

                if api_person_id:
                    print(result)
                
        frame_no += 1
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