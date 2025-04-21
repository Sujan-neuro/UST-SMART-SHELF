from utils import get_current_location

# MODEL WEIGHTS
AGE_DETECTOR_WEIGHTS = "./src/resnet50_regression.pth"
GENDER_DETECTOR = "rizvandwiki/gender-classification"

# DETAILED CONFIGURABLE ITEMS
DEFAULT_CAMERA_INDEX = 0
CONFIDENCE_THRESHOLD = 0.8
MIN_FACE_RATIO = 0.1
EMBEDDING_THRESHOLD = 0.2

# TRACKING_DURATION_SEC should be more than PROCESS_INTERVAL_SEC always
PROCESS_INTERVAL_SEC = 2
TRACKING_DURATION_SEC = 3
MAX_EMBEDDING_TO_MATCH = 500

STORE_LOCATION = get_current_location()

# SCREEN LOCATION ID
LOCATION_ID = "Paste location id here"

#KAFKA DETAILS
TOPICS = ['Paste kafka topic here']
BOOTSTRAP_SERVERS='Paste your secret server here'