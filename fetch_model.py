import urllib.request

def download_uav_model():
    print("Initiating secure connection to HuggingFace AI Hub (Public Repository)...")
    
    url = "https://huggingface.co/Javvanny/yolov8m_flying_objects_detection/resolve/main/yolov8m_fly_obj_detection.pt"
    filename = "uav_model.pt"
    
    print(f"Downloading military UAV weights to '{filename}'...")
    print("This might take a minute or two depending on your internet speed...")
    
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    
    try:
        with urllib.request.urlopen(req) as response, open(filename, 'wb') as out_file:
            out_file.write(response.read())
        print("\n[SUCCESS] Download Complete!")
        print("Your system is now armed with the new UAV detection model.")
    except Exception as e:
        print(f"\n[ERROR] Connection failed: {e}")

if __name__ == "__main__":
    download_uav_model()