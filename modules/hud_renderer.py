import cv2

class HUDRenderer:
    def __init__(self):
        """Initializes the UI settings and military color codes."""
        self.threat_colors = {
            "YUKSEK": (0, 0, 255),    # Qırmızı - maşınlar və ya yüksək təhdidlər üçün
            "ORTA": (0, 255, 255),    # Sarı - Heyət üçün
            "ASAGI": (0, 255, 0)      # Yaşıl - Sıradan obyektlər üçün
        }

    def draw_overlay(self, frame, detections, fps):
        """
        Takes the raw video frame and the AI detections, draws the tactical UI, 
        and returns the finished frame to be displayed.
        """
        height, width, _ = frame.shape
        threat_detected = len(detections) > 0

        for target in detections:
            x1, y1, x2, y2 = target["box"]
            t_level = target["threat_level"]
            color = self.threat_colors.get(t_level, (0, 255, 0))

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            label = f"[{target['class_name']}] {t_level} ({target['confidence']}%)"
            cv2.putText(frame, label, (x1, max(20, y1 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        sys_color = (0, 0, 255) if threat_detected else (0, 255, 0)
        sys_text = "STATUS: HEDEF ASKARLANDI" if threat_detected else "STATUS: TEMIZ"
        
        cv2.putText(frame, f"FPS: {fps}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, sys_text, (20, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.7, sys_color, 2)
        cv2.putText(frame, "NETWORK: AIR-GAPPED (OFFLINE)", (20, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        center_x, center_y = width // 2, height // 2
        cv2.line(frame, (center_x - 20, center_y), (center_x + 20, center_y), (0, 255, 0), 1)
        cv2.line(frame, (center_x, center_y - 20), (center_x, center_y + 20), (0, 255, 0), 1)

        return frame