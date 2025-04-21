from sklearn.metrics.pairwise import cosine_similarity
import time, datetime
from collections import OrderedDict
import geocoder
import cv2

def list_available_cameras(max_tested=5):
    available_cameras = []
    for index in range(max_tested):
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            available_cameras.append(index)
            cap.release()
    return available_cameras


def cosine_distance(vec1, vec2):
    return 1 - cosine_similarity([vec1], [vec2])[0][0]


# class IDTracker:
#     def __init__(self, tracking_duration_sec = 3):
#         self.last_person_id = None  # To track the last person ID
#         self.last_person_appeared_time = 0  # Timestamp when the last person appeared
#         self.already_printed_person_id = None  # To ensure no consecutive persons being returned
#         self.tracking_duration_sec = tracking_duration_sec # Duration for tracking a person continuously

#     def check_for_api(self, current_id):
#         current_time = time.time()  # Get the current timestamp
#         person_id_found = False

#         # If the person ID has changed
#         if self.last_person_id != current_id:
#             self.last_person_appeared = current_time  # Reset the timer
#             self.last_person_id = current_id  # Update the last person ID

#         # If the current person has not printed consecutively
#         if current_id != self.already_printed_person_id:
#             if current_time - self.last_person_appeared_time >= self.tracking_duration_sec:
#                 person_id_found = current_id
#                 self.already_printed_person_id = current_id  # Mark this person as printed
#         return person_id_found

class IDTracker:
    """
    A class to track how long a detected person ID has stayed and trigger an action
    only if the person stays for at least `tracking_duration_sec`.

    Attributes:
    -----------
    tracking_duration_sec : int
        The required duration (in seconds) a person must stay to trigger.
    last_person_id : str or int or None
        The last detected person ID.
    last_person_appeared_time : float
        Timestamp when the current person ID first appeared.
    last_trigger_time : float
        Timestamp when the last successful trigger occurred.

    Methods:
    --------
    check_for_api(current_id: str or int) -> str or int or bool
        Checks if the current ID has stayed enough time to be triggered.
    """

    def __init__(self, tracking_duration_sec: int = 3):
        """
        Initializes the IDTracker.

        Parameters:
        -----------
        tracking_duration_sec : int, optional
            Number of seconds a person must stay to trigger output (default is 3).
        """
        self.tracking_duration_sec = tracking_duration_sec
        self.last_person_id = None
        self.last_person_appeared_time = 0.0
        self.last_trigger_time = 0.0

    def check_for_api(self, current_id) -> str | int | bool:
        """
        Check if the given ID has stayed long enough to trigger.

        Parameters:
        -----------
        current_id : str or int
            The ID of the current detected person.

        Returns:
        --------
        str or int:
            Returns the `current_id` if the stay duration condition is met.
        bool:
            Returns False if conditions are not yet met.
        """
        try:
            current_time = time.time()

            # Reset timer if new ID appears
            if self.last_person_id != current_id:
                self.last_person_id = current_id
                self.last_person_appeared_time = current_time
                self.last_trigger_time = 0.0

            # Check if the person stayed enough and if it's time to trigger again
            if (current_time - self.last_person_appeared_time) >= self.tracking_duration_sec:
                if (current_time - self.last_trigger_time) >= self.tracking_duration_sec:
                    self.last_trigger_time = current_time
                    return current_id

            return False

        except Exception as e:
            print(f"[ERROR] IDTracker.check_for_api encountered an error: {e}")
            return False


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
    
    
# Age destandardization class
class DestandardizeAge:
    def __init__(self):
        self.mean_age = 31.11096921925228
        self.std_age = 17.220405909006107

    def destandardize_age(self, standardized_age):
        return standardized_age * self.std_age + self.mean_age
    
    
def get_current_location():
    location_data = {
        "lat": '',
        "lng": '',
        "x": [''],
        "y": ['']
        }
    try:
        g = geocoder.ip('me')  # Get current location based on IP
        if g.latlng:
            lat, lng = g.latlng
            x = ['']  
            y = [''] 
            location_data = {
                "lat": str(lat),
                "lng": str(lng),
                "x": x,
                "y": y
            }
            return location_data
        else:
            return location_data
    except:
        return location_data