ID2LABEL = {
    0: "0-2",
    1: "3-9",
    2: "10-19",
    3: "20-29",
    4: "30-39",
    5: "40-49",
    6: "50-59",
    7: "60-69",
    8: "more than 70",
}

AGE_DETECTOR = "nateraw/vit-age-classifier"
GENDER_DETECTOR = "rizvandwiki/gender-classification"
PEOPLE_DETECTOR = "yolov8m.pt"
CONFIDENCE_THRESHOLD = 0.8
EMBEDDING_THRESHOLD = 0.18
# TRACKING_DURATION_SEC should be more than PROCESS_INTERVAL_SEC always
PROCESS_INTERVAL_SEC = 2
TRACKING_DURATION_SEC = 3
MAX_EMBEDDING_TO_MATCH = 500
LOCATION_ID = "6643631e2fd6df5a3e669233"