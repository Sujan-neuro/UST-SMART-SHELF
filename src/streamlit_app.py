import time
import json
import cv2
import streamlit as st
from main import FaceProcessor
from streamlit_utils import set_page_style, display_header, sidebar_config
from kafka_producer import send_to_kafka
from config import TOPICS


set_page_style()
display_header()

# Initialize session
if "run_loop" not in st.session_state:
    st.session_state.run_loop = False
if "detection_log" not in st.session_state:
    st.session_state.detection_log = []

# Get sidebar config
config = sidebar_config()

# Start or stop control
if config["run"]:
    st.session_state.run_loop = True

frame_placeholder = st.empty()
log_placeholder = st.empty()

identify_age=config["identify_age"]
identify_gender=config["identify_gender"]

face_processor = FaceProcessor(
    process_interval_sec=config["process_interval_sec"],
    tracking_duration_sec=config["tracking_duration_sec"],
    confidence_threshold=config["confidence_threshold"],
    min_face_ratio=config["min_face_ratio"],
    default_camera_index=config["default_camera_index"],
    identify_age=identify_age,
    identify_gender=identify_gender
)

# Main loop
if st.session_state.run_loop:
    st.success("Smart Shelf is running. Press 'STOP' to end.")
    while st.session_state.run_loop:
        ret, frame = face_processor.cap.read()
        if not ret:
            st.error("Failed to retrieve frame. Exiting...")
            st.session_state.run_loop = False
            break

        bbox, result = face_processor.processor.process_frame(frame)
        if result:
            current_time = time.time()
            if current_time - face_processor.last_save_time > config["process_interval_sec"]:
                if face_processor.output_location:
                    with open(face_processor.output_location, "a") as f:
                        f.write(json.dumps(result) + "\n")
                    face_processor.last_save_time = current_time

            age = result.get("age", "Neutral")
            gender = result.get("gender", "Neutral")
            x1, y1, x2, y2 = map(int, bbox)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 4)

            try:
                if age == 0:
                    age = "Neutral"
                elif age < 20:
                    age = "below 20"
                elif age > 60:
                    age = "above 60"
                else:
                    age = f"{age-5}-{age+5}"
            except:
                age = "Neutral"

            label = f"Age: {age} | Gender: {gender}"


            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 3)

            person_id = result["visitorId"]
            if face_processor.tracker.check_for_api(person_id):
                print(result)

                # Add log entry
                log_entry = f"Time: {result.get('visitTime', 'None')} | Age: {age} | Gender: {gender}"
                st.session_state.detection_log.append(log_entry)

                # Keep displaying all logs in scrollable text area
                log_text = "\n".join(reversed(st.session_state.detection_log))  # latest on top
                log_placeholder.text_area("Detection Log", value=log_text, height=300, disabled=True)
                send_to_kafka(result, TOPICS)
                # if (identify_age and identify_gender):
                #     send_to_kafka(result, DETECTION_TOPICS)
                # elif (not identify_age and not identify_gender):
                #     send_to_kafka(result, NO_DETECTION_TOPICS)

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_placeholder.image(frame_rgb, channels="RGB")

        if config["stop"]:
            st.session_state.run_loop = False
            break

    face_processor.cap.release()
    st.info("Smart Shelf stopped. Press RUN from the sidebar to restart.")
else:
    st.info("Press RUN from the sidebar to start Smart Shelf.")