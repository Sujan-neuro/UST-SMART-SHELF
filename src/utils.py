from sklearn.metrics.pairwise import cosine_similarity
import time, datetime
from collections import OrderedDict
import geocoder

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
    
# Age destandardization class
class DestandardizeAge:
    def __init__(self):
        self.mean_age = 30.43709706303725
        self.std_age = 16.547361149730804

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