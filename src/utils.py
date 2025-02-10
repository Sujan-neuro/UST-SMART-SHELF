from sklearn.metrics.pairwise import cosine_similarity
import time, datetime, cv2
from collections import OrderedDict

def cosine_distance(vec1, vec2):
    return 1 - cosine_similarity([vec1], [vec2])[0][0]

class IDTracker:
    def __init__(self, tracking_duration_sec = 3):
        self.last_person_id = None  # To track the last person ID
        self.last_person_appeared_time = 0  # Timestamp when the last person appeared
        self.already_printed_person_id = None  # To ensure no consecutive persons being returned
        self.tracking_duration_sec = tracking_duration_sec # Duration for tracking a person continuously

    def check_for_api(self, current_id):
        current_time = time.time()  # Get the current timestamp
        person_id_found = False

        # If the person ID has changed
        if self.last_person_id != current_id:
            self.last_person_appeared = current_time  # Reset the timer
            self.last_person_id = current_id  # Update the last person ID

        # If the current person has not printed consecutively
        if current_id != self.already_printed_person_id:
            if current_time - self.last_person_appeared_time >= self.tracking_duration_sec:
                person_id_found = current_id
                self.already_printed_person_id = current_id  # Mark this person as printed
        return person_id_found
    

class LimitedDict(OrderedDict):
    def __init__(self, max_size=500, *args, **kwargs):
        self.max_size = max_size
        super().__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        if len(self) >= self.max_size:
            self.popitem(last=False)  # Remove the oldest item (FIFO)
        super().__setitem__(key, value)


class DailyIndex:
    def __init__(self):
        self.previous_date = datetime.date.today()
        self.index = 0  # Start index

    def get_index(self):
        current_date = datetime.date.today()

        # Reset index if the day has changed
        if self.previous_date != current_date:
            self.index = 1
            self.previous_date = current_date
        else:
            self.index += 1

        return self.index
    
class CameraFPS:
    def __init__(self, cap, duration = 2):
        self.cap = cap
        self.duration = duration  # Time to measure FPS
        self.fps_counter = 0
        self.start_time = time.time()

    def calculate_fps(self):
        """Capture frames and calculate the average FPS over the duration."""
        start_time = time.time()
        
        while time.time() - start_time < self.duration:
            ret, _ = self.cap.read()
            if not ret:
                break
            self.fps_counter += 1
        
        elapsed_time = time.time() - start_time
        avg_fps = self.fps_counter / elapsed_time if elapsed_time > 0 else 0
        
        return int(avg_fps)