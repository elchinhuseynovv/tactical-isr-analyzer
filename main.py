import cv2
import time

from modules.vision_engine import VisionEngine
from modules.hud_renderer import HUDRenderer
from modules.telemetry_logger import TelemetryLogger

def main():
    print("Sistem Yüklənir: Taktiki Edge AI (Modulyar Sistem)...")
    
    vision = VisionEngine(model_path="yolov8m_defence.pt")
    hud = HUDRenderer()
    logger = TelemetryLogger(log_dir="logs")

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    if not cap.isOpened():
        print("Xəta: PC kamerası açılmadı.")
        return

    print("Sistem Aktivdir.")
    print("-> Çıxmaq üçün 'Q' düyməsini basın.")
    print("-> Termal kameraya keçmək üçün 'T' düyməsini basın.")
    print("-> Müharibə rejimi (Domain Override) üçün 'M' düyməsini basın.")

    thermal_mode = False 
    combat_mode = False

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        start_time = time.time()

        detections, kill_box = vision.process_frame(frame, combat_mode=combat_mode)
        logger.log_detections(detections)

        fps = int(1.0 / (time.time() - start_time))
        output_frame = hud.draw_overlay(frame, detections, kill_box, fps, thermal_mode)
        if combat_mode:
            cv2.putText(output_frame,"MUHARIBE REJIMI: AKTIV (OVERRIDE)", (30, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.imshow("Taktiki Izleme Merkezi", output_frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('t'):
            thermal_mode = not thermal_mode
        elif key == ord('m'):
            combat_mode = not combat_mode

    cap.release()
    cv2.destroyAllWindows()
    logger.close()
    print("Sistem söndürüldü.")

if __name__ == "__main__":
    main()