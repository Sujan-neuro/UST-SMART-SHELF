from sklearn.metrics.pairwise import cosine_similarity
import time


def cosine_distance(vec1, vec2):
    return 1 - cosine_similarity([vec1], [vec2])[0][0]

class IDTracker:
    def __init__(self):
        self.last_person_id = None  # To track the last person ID
        self.last_person_appeared = 0  # Timestamp when the last person appeared
        self.already_printed_person_id = None  # To ensure no consecutive winners

    def check_for_api(self, current_id):
        current_time = time.time()  # Get the current timestamp
        person_id_found = False

        # If the person ID has changed
        if self.last_person_id != current_id:
            self.last_person_appeared = current_time  # Reset the timer
            self.last_person_id = current_id  # Update the last person ID

        # If the current person has not won consecutively
        if current_id != self.already_printed_person_id:
            if current_time - self.last_person_appeared >= 3:
                person_id_found = current_id
                self.already_printed_person_id = current_id  # Mark this person as printed
        return person_id_found




