import time
import json
import cv2
import streamlit as st
from main import FaceProcessor  # Adjust the import path as needed
from kafka_producer import send_to_kafka  # if used by FaceProcessor
from config import (
    PROCESS_INTERVAL_SEC,
    TRACKING_DURATION_SEC,
    CONFIDENCE_THRESHOLD,
    MIN_FACE_RATIO
)
from utils import list_available_cameras

# Fetching the list of cameras
camera_list = list_available_cameras(max_tested = 10)

# Initialize session state variable to control the loop
if "run_loop" not in st.session_state:
    st.session_state.run_loop = False

st.title("Smart Shelf")

# Sidebar suggestion and configuration header
st.sidebar.header("Face Processor Configuration")

# Dropdowns for identification options
identify_age_option = st.sidebar.selectbox(
    "Identify Age", options=[True, False], index=1, help="Enable or disable age identification."
)
identify_gender_option = st.sidebar.selectbox(
    "Identify Gender", options=[True, False], index=1, help="Enable or disable gender identification."
)

default_camera_index = st.sidebar.selectbox(
    "Default Camera Index",
    options=camera_list,
    index=0,  # Default to the first option
    help="Select the index of the default camera."
)

# Output location for JSON results (leave empty for False)
output_location_input = st.sidebar.text_input(
    "Output Location (Example: output.json or empty)",
    value="",
    help="Enter a file path to save JSON results or leave empty."
)
output_location = output_location_input.strip() if output_location_input.strip() != "" else False

st.sidebar.markdown("**Suggestion:** The parameters below are optimised. Changing them is not recommended.")
# Additional configurable parameters with default values shown as strings
process_interval_sec = st.sidebar.text_input(
    "Process Interval (sec)",
    value=str(PROCESS_INTERVAL_SEC),
    help="Time interval between processing frames. (Optimised default provided)"
)
tracking_duration_sec = st.sidebar.text_input(
    "Tracking Duration (sec)",
    value=str(TRACKING_DURATION_SEC),
    help="Duration for tracking a face. (Optimised default provided)"
)
confidence_threshold = st.sidebar.text_input(
    "Confidence Threshold (0 to 1)",
    value=str(CONFIDENCE_THRESHOLD),
    help="Confidence threshold for detection. (Optimised default provided)"
)
min_face_ratio = st.sidebar.text_input(
    "Minimum Face Ratio ( 0 to 1)",
    value=str(MIN_FACE_RATIO),
    help="Minimum face ratio. (Optimised default provided)"
)
process_interval_sec = int(process_interval_sec)
tracking_duration_sec = int(tracking_duration_sec)
confidence_threshold = float(confidence_threshold)
min_face_ratio = float(min_face_ratio)

# Buttons to start and stop the identification loop
start_button = st.sidebar.button("IDENTIFY")
stop_button = st.sidebar.button("STOP")

# When IDENTIFY is clicked, set the run flag in session state
if start_button:
    st.session_state.run_loop = True

# Initialize the FaceProcessor with both default and user-specified parameters
face_processor = FaceProcessor(
    process_interval_sec=process_interval_sec,
    tracking_duration_sec=tracking_duration_sec,
    confidence_threshold=confidence_threshold,
    min_face_ratio=min_face_ratio,
    default_camera_index=default_camera_index,
    identify_age=identify_age_option,
    identify_gender=identify_gender_option,
    output_location=output_location
)

# Placeholder for displaying the video feed
frame_placeholder = st.empty()

# Main processing loop: runs only if the run_loop flag is set to True
if st.session_state.run_loop:
    st.write("Smart Shelf is running. Press 'STOP' to end.")
    while st.session_state.run_loop:
        ret, frame = face_processor.cap.read()
        if not ret:
            st.write("Failed to retrieve frame. Exiting...")
            st.session_state.run_loop = False
            break

        # Process the frame and annotate if results are available
        bbox_coordinate, result = face_processor.processor.process_frame(frame)
        if result:
            current_time = time.time()
            if current_time - face_processor.last_save_time > face_processor.process_interval_sec:
                if face_processor.output_location:
                    with open(face_processor.output_location, "a") as f:
                        f.write(json.dumps(result) + "\n")
                    face_processor.last_save_time = current_time

            predicted_age = result.get("age", "Neutral")
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
                predicted_age = "Neutral"

            text = f"Age:{predicted_age} || Gender:{predicted_gender}"
            cv2.putText(frame, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.8, (0, 255, 0), 3, cv2.LINE_AA)

            person_id = result["visitorId"]
            api_person_id = face_processor.tracker.check_for_api(person_id)
            if api_person_id:
                print(result)
                # send_to_kafka(result)
                ################################## Only for AWS event ###########################
                if face_processor.identify_age or face_processor.identify_gender:
                    topic = "aws_lab_no_detection"
                    send_to_kafka(result, topics=[topic])
                if face_processor.identify_age and face_processor.identify_gender:
                    topic = "aws_lab_default"
                    send_to_kafka(result, topics=[topic])
                #################################################################################

        # Convert frame from BGR to RGB and update the Streamlit image placeholder
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_placeholder.image(frame_rgb, channels = "RGB")

        # Check if STOP was pressed to exit the loop
        if stop_button:
            st.session_state.run_loop = False
            break

    face_processor.cap.release()
    st.write("Press IDENTIFY from the sidebar to restart Smart Shelf.")
else:
    st.write("Press IDENTIFY from the sidebar to start Smart Shelf.")
