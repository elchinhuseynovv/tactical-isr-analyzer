import csv
import os
from datetime import datetime

class TelemetryLogger:
    def __init__(self, log_dir="logs"):
        """Initializes the logging system and creates a new CSV file for the mission."""
        self.log_dir = log_dir
        
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.filepath = os.path.join(self.log_dir, f"mission_log_{timestamp}.csv")
        
        self.file = open(self.filepath, mode='w', newline='')
        self.writer = csv.writer(self.file)
        self.writer.writerow(["Timestamp", "Target Class", "Threat Level", "Confidence (%)", "Bounding Box"])

    def log_detections(self, detections):
        """Writes target data to the CSV file if any threats are detected."""
        if not detections:
            return
            
        current_time = datetime.now().strftime("%H:%M:%S.%f")[:-3] 
        
        for target in detections:
            self.writer.writerow([
                current_time,
                target["class_name"],
                target["threat_level"],
                target["confidence"],
                str(target["box"])
            ])

    def close(self):
        """Safely saves and closes the file when the system is shut down."""
        if self.file:
            self.file.close()