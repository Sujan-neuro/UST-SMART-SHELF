import time
import logging


# Setup logger
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s | DateTime: %(asctime)s | File: %(name)s | Message: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


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
            logger.error(f"IDTracker.check_for_api encountered an error: {e}")
            return False
        

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