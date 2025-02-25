from utils import get_current_location

AGE_DETECTOR_WEIGHTS = "./src/resnet50_regression.pth"
GENDER_DETECTOR = "rizvandwiki/gender-classification"
CONFIDENCE_THRESHOLD = 0.8
EMBEDDING_THRESHOLD = 0.18
# TRACKING_DURATION_SEC should be more than PROCESS_INTERVAL_SEC always
PROCESS_INTERVAL_SEC = 1
TRACKING_DURATION_SEC = 3
MAX_EMBEDDING_TO_MATCH = 500
LOCATION_ID = "6643631e2fd6df5a3e669233"

STORE_LOCATION = get_current_location()
TOPICS = ['nrf_singapore']