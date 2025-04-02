from utils import get_current_location

AGE_DETECTOR_WEIGHTS = "./src/resnet50_regression.pth"
# GENDER_DETECTOR_WEIGHTS = "./src/resnet50_classification.pth"
GENDER_DETECTOR = "rizvandwiki/gender-classification"
DEFAULT_CAMERA_INDEX = 0
CONFIDENCE_THRESHOLD = 0.8
MIN_FACE_RATIO = 0.1
EMBEDDING_THRESHOLD = 0.2
# TRACKING_DURATION_SEC should be more than PROCESS_INTERVAL_SEC always
PROCESS_INTERVAL_SEC = 2
TRACKING_DURATION_SEC = 3
MAX_EMBEDDING_TO_MATCH = 500
LOCATION_ID = "67e26a2b29853b7303244dc3"

STORE_LOCATION = get_current_location()
TOPICS = ['aws_lab_default']