from ultralytics import YOLO

class VisionEngine:
    def __init__(self, model_path="yolov8n.pt"):
        self.model = YOLO(model_path)

    def process_frame(self, frame):
        height, width = frame.shape[:2]
        kx1, ky1 = (width // 2) - 150, (height // 2) - 150
        kx2, ky2 = (width // 2) + 150, (height // 2) + 150
        kill_box = (kx1, ky1, kx2, ky2)

        results = self.model.track(source=frame, conf=0.4, persist=True, verbose=False)
        detections = []

        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                conf = int(box.conf[0] * 100)
                cls_id = int(box.cls[0])
                class_name = self.model.names[cls_id].upper()

                # yeni: the unique tracking ID by ByteTrack
                if box.id is not None:
                    track_id = int(box.id[0])
                    target_id_str = f"TRG-{track_id:03d}" # Formatlar TRG-001, TRG-002...
                else:
                    target_id_str = "TRG-???"

                if cls_id in [2, 3, 5, 7]:
                    threat_level = "YUKSEK"
                    target_type = "NEQLIYYAT"
                elif cls_id == 0:
                    threat_level = "ORTA"
                    target_type = "SEXSI HEYET"
                else:
                    threat_level = "ASAGI"
                    target_type = "UMUMI OBYEKT"

                tx1, ty1, tx2, ty2 = int(x1), int(y1), int(x2), int(y2)

                in_kill_zone = (tx1 < kx2 and tx2 > kx1 and ty1 < ky2 and ty2 > ky1)
                is_locked = bool(in_kill_zone and threat_level == "YUKSEK")

                detections.append({
                    "target_id": target_id_str,
                    "box": (tx1, ty1, tx2, ty2),
                    "confidence": conf,
                    "class_name": class_name,
                    "target_type": target_type,
                    "threat_level": threat_level,
                    "is_locked": is_locked
                })

        return detections, kill_box