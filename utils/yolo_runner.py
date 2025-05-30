import os
import requests
from PIL import Image, ImageOps
import io

YOLO_API_URL = "https://yolo-api-service-744417252774.us-central1.run.app/predict/"  # ✅ Include trailing slash

def resize_with_letterbox(image_path, size=640):
    img = Image.open(image_path).convert("RGB")
    img_resized = ImageOps.pad(img, (size, size), method=Image.BICUBIC, color=(114, 114, 114))
    buffer = io.BytesIO()
    img_resized.save(buffer, format="JPEG")
    buffer.seek(0)
    return buffer

def run_yolo_on_directory(image_dir, label_dir):
    os.makedirs(label_dir, exist_ok=True)

    for filename in os.listdir(image_dir):
        if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            continue

        image_path = os.path.join(image_dir, filename)
        label_filename = os.path.splitext(filename)[0] + ".txt"
        label_path = os.path.join(label_dir, label_filename)

        print(f"📤 Processing: {filename}")
        try:
            resized_buffer = resize_with_letterbox(image_path)
            files = {"file": ("image.jpg", resized_buffer, "image/jpeg")}  # ✅ Match Colab test

            response = requests.post(YOLO_API_URL, files=files)

            if response.status_code != 200:
                print(f"❌ Failed: {response.status_code} for {filename}")
                continue

            yolo_data = response.json().get("detections", [])
            if not yolo_data:
                print(f"⚠️ No detections: {filename}")
                continue

            with open(label_path, "w") as f:
                for det in yolo_data:
                    class_id = det["class_id"]
                    bbox = det["box"]
                    f.write(f"{class_id} {' '.join(str(round(x, 6)) for x in bbox)}\n")

            print(f"✅ Saved: {label_path}")

        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")
