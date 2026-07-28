import csv
import os
from datetime import datetime

class TelemetryLogger:
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.filepath = os.path.join(self.log_dir, f"mission_log_{timestamp}.csv")
        
        self.file = open(self.filepath, mode='w', newline='')
        self.writer = csv.writer(self.file)
        # Added 'Lock Status' to the CSV columns
        self.writer.writerow(["Timestamp", "Target Class", "Threat Level", "Confidence (%)", "Lock Status", "Bounding Box"])

    def log_detections(self, detections):
        if not detections:
            return 
            
        current_time = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        for target in detections:
            is_locked = "YES" if target.get("is_locked", False) else "NO"
            
            self.writer.writerow([
                current_time,
                target["class_name"],
                target["threat_level"],
                target["confidence"],
                is_locked,
                str(target["box"])
            ])

    def close(self):
        if self.file:
            self.file.close()