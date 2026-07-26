import cv2
import time
from ultralytics import YOLO


print("Sistem Yüklənir: Taktiki Edge AI (YOLOv8n)...")
# On the very first run, this downloads a tiny (~6MB) weights file.
# After that, it runs 100% offline. 'n' stands for nano (fastest version).
model = YOLO("yolov8n.pt") 

print("Taktiki HUD İnisializasiya olunur...")
cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

if not cap.isOpened():
    print("Xəta: PC kamerası açılmadı.")
    exit()

print("Sistem Aktivdir. Çıxmaq üçün 'Q' düyməsini basın.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    start_time = time.time()
    height, width, _ = frame.shape

    # --- RUN YOLOv8 INFERENCE ---
    # conf=0.4 means we only highlight targets the AI is 40%+ sure about
    # verbose=False stops the terminal from being flooded with text
    results = model.predict(source=frame, conf=0.4, verbose=False)

    threat_detected = False

    for result in results:
        boxes = result.boxes
        for box in boxes:
            threat_detected = True
            
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

            conf = int(box.conf[0] * 100)
            cls_id = int(box.cls[0])
            class_name = model.names[cls_id].upper()

            # Military Threat Logic based on COCO classes
            # 0: person, 2: car, 3: motorcycle, 5: bus, 7: truck
            if cls_id in [2, 3, 5, 7]:
                color = (0, 0, 255) # Red for Vehicles
                threat_level = "YUKSEK (Neqliyyat)"
            elif cls_id == 0:
                color = (0, 255, 255) # Yellow for Personnel
                threat_level = "ORTA (Sexsi heyet)"
            else:
                color = (0, 255, 0) # Green for generic objects
                threat_level = "ASAGI"

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            label = f"[{class_name}] CONF: {conf}%"
            cv2.putText(frame, label, (x1, max(20, y1 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    fps = int(1.0 / (time.time() - start_time))
    sys_color = (0, 0, 255) if threat_detected else (0, 255, 0)
    sys_text = "STATUS: HEDEF ASKARLANDI" if threat_detected else "STATUS: TEMIZ"
    
    cv2.putText(frame, f"FPS: {fps}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(frame, sys_text, (20, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.7, sys_color, 2)
    cv2.putText(frame, "NETWORK: AIR-GAPPED (OFFLINE)", (20, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    center_x, center_y = width // 2, height // 2
    cv2.line(frame, (center_x - 20, center_y), (center_x + 20, center_y), (0, 255, 0), 1)
    cv2.line(frame, (center_x, center_y - 20), (center_x, center_y + 20), (0, 255, 0), 1)

    cv2.imshow("Taktiki Izləmə", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()