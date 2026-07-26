import cv2
import json
import threading
import time
from PIL import Image
from google import genai
from google.genai import types

try:
    client = genai.Client()
except Exception as e:
    print("API Error: Please make sure GEMINI_API_KEY is set in your terminal.")
    exit()

ISR_SYSTEM_PROMPT = """
Siz taktiki komandanlıq sistemi daxilində fəaliyyət göstərən qabaqcıl PUA kəşfiyyatı (ISR) süni intellekt köməkçisisiniz.
Aşağıdakı struktura uyğun YALNIZ düzgün (valid) JSON formatında cavab verin:
{
  "status": "HƏDƏF_AŞKARLANDI və ya TƏMİZ",
  "threat_level": "AŞAĞI, ORTA, YÜKSƏK, və ya NAMƏLUM",
  "targets": [
    {
      "type": "Məsələn: Zirehli texnika / Şəxsi heyət / Bina",
      "count": 1,
      "box_2d": [ymin, xmin, ymax, xmax], 
      "description": "Qısa əməliyyat təsviri"
    }
  ],
  "terrain_assessment": "Ətraf mühit və relyef haqqında qısa qeyd"
}
ÖNƏMLİ: 'box_2d' dəyərləri 0 ilə 1000 arasındadır (0,0 yuxarı sol, 1000,1000 aşağı sağ). Əgər hədəf yoxdursa, 'targets' massivini boş saxlayın.
"""
latest_report = None
is_analyzing = False
last_analysis_time = time.time()
ANALYSIS_INTERVAL = 4 # Seconds between AI scans

def analyze_frame_background(frame_bgr):
    """Background thread to process the AI request without freezing the video."""
    global latest_report, is_analyzing
    is_analyzing = True
    
    # Convert OpenCV BGR to standard RGB for Gemini
    frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(frame_rgb)
    
    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash", 
            contents=[pil_image, "Taktiki ISR analizi aparin."],
            config=types.GenerateContentConfig(
                system_instruction=ISR_SYSTEM_PROMPT,
                response_mime_type="application/json",
                temperature=0.2 
            )
        )
        latest_report = json.loads(response.text)
    except Exception as e:
        print(f"Background AI Error: {e}")
    finally:
        is_analyzing = False

print("Initializing Tactical HUD...")
cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

if not cap.isOpened():
    print("Error: Could not open PC camera.")
    exit()

print("Camera active. Press 'Q' to exit.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    height, width, _ = frame.shape
    current_time = time.time()

    if (current_time - last_analysis_time) >= ANALYSIS_INTERVAL:
        if not is_analyzing:
            # Pass a copy of the frame to the background thread
            thread = threading.Thread(target=analyze_frame_background, args=(frame.copy(),))
            thread.start()
            last_analysis_time = current_time

    status_color = (0, 165, 255) if is_analyzing else (0, 255, 0) # Orange if analyzing, Green if ready
    sys_text = "AI STATUS: SCANNING..." if is_analyzing else "AI STATUS: ACTIVE"
    cv2.putText(frame, sys_text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)

    if latest_report:
        threat_level = latest_report.get("threat_level", "NAMELUM")
        t_color = (0, 0, 255) if threat_level == "YUKSEK" else (0, 255, 255) # Red for High, Yellow for others
        
        cv2.putText(frame, f"THREAT LEVEL: {threat_level}", (20, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.7, t_color, 2)
        cv2.putText(frame, f"STATUS: {latest_report.get('status', '')}", (20, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, t_color, 2)

        for target in latest_report.get("targets", []):
            if "box_2d" in target and len(target["box_2d"]) == 4:
                ymin, xmin, ymax, xmax = target["box_2d"]
                
                left = int((xmin / 1000) * width)
                top = int((ymin / 1000) * height)
                right = int((xmax / 1000) * width)
                bottom = int((ymax / 1000) * height)
                
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 3)
                
                label = f"{target.get('type', 'HEDEF')}"
                cv2.putText(frame, label, (left, max(30, top - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    center_x, center_y = width // 2, height // 2
    cv2.line(frame, (center_x - 20, center_y), (center_x + 20, center_y), (0, 255, 0), 1)
    cv2.line(frame, (center_x, center_y - 20), (center_x, center_y + 20), (0, 255, 0), 1)

    cv2.imshow("Taktiki PUA Merkezi", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()