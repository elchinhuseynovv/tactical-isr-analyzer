import cv2

class HUDRenderer:
    def __init__(self):
        self.threat_colors = {
            "YUKSEK": (0, 0, 255),    
            "ORTA": (0, 255, 255),    
            "ASAGI": (0, 255, 0)      
        }

    def draw_overlay(self, frame, detections, kill_box, fps, thermal_mode=False):
        height, width, _ = frame.shape
        
        system_locked = any(d.get("is_locked", False) for d in detections)
        threat_detected = len(detections) > 0

        if thermal_mode:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frame = cv2.applyColorMap(gray, cv2.COLORMAP_JET)

        kx1, ky1, kx2, ky2 = kill_box
        box_color = (0, 0, 255) if system_locked else (0, 255, 255)
        cv2.rectangle(frame, (kx1, ky1), (kx2, ky2), box_color, 1)
        cv2.putText(frame, "ENGAGEMENT ZONE", (kx1, ky1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, box_color, 1)

        for target in detections:
            x1, y1, x2, y2 = target["box"]
            t_level = target["threat_level"]
            is_locked = target.get("is_locked", False)
            color = self.threat_colors.get(t_level, (0, 255, 0))

            if is_locked:
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 4)
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                cv2.drawMarker(frame, (cx, cy), (0, 0, 255), cv2.MARKER_CROSS, 20, 2)
                cv2.putText(frame, "LOCKED", (x1, y2 + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            else:
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            label = f"[{target['class_name']}] {t_level} ({target['confidence']}%)"
            cv2.putText(frame, label, (x1, max(20, y1 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        if system_locked:
            sys_color = (0, 0, 255)
            sys_text = "CRITICAL: TARGET LOCKED!"
            cv2.putText(frame, "TARGET LOCKED", (width//2 - 120, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
        elif threat_detected:
            sys_color = (0, 165, 255)
            sys_text = "STATUS: HEDEF ASKARLANDI"
        else:
            sys_color = (0, 255, 0)
            sys_text = "STATUS: TEMIZ"
        
        cam_mode = "SENSOR: FLIR (THERMAL)" if thermal_mode else "SENSOR: RGB (STANDARD)"
        cv2.putText(frame, f"FPS: {fps}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, sys_text, (20, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.7, sys_color, 2)
        cv2.putText(frame, cam_mode, (20, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        return frame