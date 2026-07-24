import os
import cv2
import json
import streamlit as st
from PIL import Image
from google import genai
from google.genai import types


try:
    client = genai.Client()
except Exception as e:
    st.error("API Error: Please make sure GEMINI_API_KEY is set in your terminal.")

ISR_SYSTEM_PROMPT = """
Siz taktiki komandanlıq sistemi daxilində fəaliyyət göstərən qabaqcıl PUA kəşfiyyatı (ISR) süni intellekt köməkçisisiniz.
Vəzifəniz verilmiş hava kadrlarını analiz etmək və Azərbaycan dilində strukturlaşdırılmış hesabat yaratmaqdır.

Aşağıdakı struktura uyğun YALNIZ düzgün (valid) JSON formatında cavab verin. Heç bir əlavə mətn yazmayın:
{
  "status": "HƏDƏF_AŞKARLANDI və ya TƏMİZ",
  "threat_level": "AŞAĞI, ORTA, YÜKSƏK, və ya NAMƏLUM",
  "targets": [
    {
      "type": "Məsələn: Zirehli texnika / Şəxsi heyət / Bina",
      "count": 1,
      "location": "Məsələn: Yuxarı-Sağ / Mərkəz",
      "description": "Qısa əməliyyat təsviri"
    }
  ],
  "terrain_assessment": "Ətraf mühit və relyef haqqında qısa qeyd",
  "recommended_action": "Məsələn: Müşahidəni davam etdir / Koordinatları göndər"
}
"""

st.set_page_config(page_title="Taktiki PUA Kəşfiyyat Analizatoru", layout="wide")
st.title("PUA (Dron) Kəşfiyyatı və Analiz Platforması")
st.caption("Avtomatlaşdırılmış Kadr Çıxarışı və Taktiki Telemetriya Sistemi")

st.sidebar.header("Sistem Idarəetməsi")
video_file = st.sidebar.file_uploader("Kəşfiyyat Videosunu Yüklə (.mp4)", type=["mp4", "avi", "mov"])
frame_interval = st.sidebar.slider("Kadr Çıxarış İntervalı (Saniyə)", 1, 10, 3)
max_frames = st.sidebar.slider("Analiz ediləcək kadrların maksimal sayı", 1, 10, 3)

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Canlı Video və Analiz Paneli")
    if video_file is not None:
        temp_video_path = "temp_uav_feed.mp4"
        with open(temp_video_path, "wb") as f:
            f.write(video_file.read())
        st.video(temp_video_path)
        
        if st.button("Taktiki Analizə Başla", use_container_width=True):
            with col2:
                st.subheader("Kəşfiyyat Jurnalı (SITREP)")
                analysis_placeholder = st.empty()
            
            with st.spinner("Kadrlar çıxarılır və analiz edilir..."):
                cap = cv2.VideoCapture(temp_video_path)
                fps = cap.get(cv2.CAP_PROP_FPS)
                frame_skip = int(fps * frame_interval)

                frame_count = 0
                analyzed_count = 0

                while cap.isOpened() and analyzed_count < max_frames:
                    ret, frame = cap.read()
                    if not ret:
                        break

                    if frame_count % frame_skip == 0:
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        pil_image = Image.fromarray(frame_rgb)

                        st.image(pil_image, caption=f"Kadr {analyzed_count + 1} (Zaman: {frame_count//fps} san)", use_container_width=True)

                        try:
                            response = client.models.generate_content(
                                model="gemini-2.5-flash",
                                contents=[pil_image, "Bu kadrı taktiki ISR protokollarına əsasən analiz et."],
                                config=types.GenerateContentConfig(
                                    system_instruction=ISR_SYSTEM_PROMPT,
                                    response_mime_type="application/json",
                                    temperature=0.2 
                                )
                            )
                            report_json = json.loads(response.text)
                            with col2:
                                with st.expander(f"Zaman: {frame_count//fps} saniyə - {report_json.get('status', 'BİLİNMİR')}", expanded=True):
                                    st.json(report_json)
                                    
                        except Exception as e:
                            st.error(f"Xəta baş verdi (Error): {e}")
                            
                        analyzed_count += 1
                        
                    frame_count += 1
                cap.release()
                st.success("Taktiki analiz tamamlandı.")
    else:
        st.info("Taktiki operatordan video axını gözlənilir...")

with col2:
    st.subheader("Kəşfiyyat Jurnalı (SITREP)")
    st.write("Hədəf qeydləri və avtomatlaşdırılmış ərazi qiymətləndirmələri burada görünəcək.")