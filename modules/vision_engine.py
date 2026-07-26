from ultralytics import YOLO

class VisionEngine:
    def __init__(self, model_path="yolov8n.pt"):
        """Initializes the AI model when the system starts."""
        self.model = YOLO(model_path)

    def process_frame(self, frame):
        """
        Takes a video frame, runs YOLOv8 inference, and returns a structured list 
        of detected targets and their tactical threat levels.
        """
        results = self.model.predict(source=frame, conf=0.4, verbose=False)
        
        detections = []

        for result in results:
            boxes = result.boxes
            for box in boxes:
                # 1. Kordinatları al
                x1, y1, x2, y2 = box.xyxy[0]

                conf = int(box.conf[0] * 100)
                cls_id = int(box.cls[0])
                class_name = self.model.names[cls_id].upper()

                # 3. Assess Threat Level based on Military Logic (COCO dataset)
                # 0: person, 2: car, 3: motorcycle, 5: bus, 7: truck
                if cls_id in [2, 3, 5, 7]:
                    threat_level = "YUKSEK"
                    target_type = "NEQLIYYAT"
                elif cls_id == 0:
                    threat_level = "ORTA"
                    target_type = "SEXSI HEYET"
                else:
                    threat_level = "ASAGI"
                    target_type = "UMUMI OBYEKT"

                detections.append({
                    "box": (int(x1), int(y1), int(x2), int(y2)),
                    "confidence": conf,
                    "class_name": class_name,
                    "target_type": target_type,
                    "threat_level": threat_level
                })

        return detections