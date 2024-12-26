import os
import json
from datetime import datetime


def save_log(LOG_FOLDER, instructions, row, image_contents):
    """
    Saves the provided instructions, row data, and image contents to a log file
    with the current timestamp.
    """
    os.makedirs(LOG_FOLDER, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"log_{timestamp}.json"
    log_path = os.path.join(LOG_FOLDER, log_filename)
    
    log_data = {
        "timestamp": timestamp,
        "instructions": instructions,
        "row": row,
        "image_contents": image_contents
    }
    
    with open(log_path, 'w') as log_file:
        json.dump(log_data, log_file, indent=4)
