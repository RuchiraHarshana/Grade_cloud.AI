#this is used to  get cropped question numbers and predict tem using model endpoint and save csv this is step5


import os
import base64
import requests
import pandas as pd

# === CONFIG ===
QUESTION_FOLDER = r"D:\final year project\backend\static\cropped_questions_to_predict"
YOLO_LABEL_FOLDER = r"D:\final year project\backend\static\yolo_labels"
OUTPUT_CSV = r"D:\final year project\backend\predicted_question_numbers.csv"
API_URL = "https://question-classifier-service-744417252774.us-central1.run.app/predict"

# === Helper: Extract YOLO metadata ===
def read_yolo_line_data(label_path, region_index):
    if not os.path.exists(label_path):
        return {}

    with open(label_path, 'r') as f:
        lines = f.readlines()

    count = -1
    for line in lines:
        parts = line.strip().split()
        if len(parts) < 5:
            continue
        class_id = int(float(parts[0]))
        if class_id != 1:
            continue
        count += 1
        if count == region_index:
            return {
                "x_center": round(float(parts[1]), 6),
                "y_center": round(float(parts[2]), 6),
                "width": round(float(parts[3]), 6),
                "height": round(float(parts[4]), 6)
            }
    return {}

# === Helper: Convert image to base64 ===
def encode_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

# === Main Execution ===
results = []
question_images = sorted([
    f for f in os.listdir(QUESTION_FOLDER)
    if f.lower().endswith((".jpg", ".jpeg", ".png"))
])

print(f"🔍 Found {len(question_images)} cropped question images...")

for file_name in question_images:
    image_path = os.path.join(QUESTION_FOLDER, file_name)

    try:
        # e.g., IMG_3975_1_245.jpg
        parts = file_name.replace(".jpg", "").replace(".jpeg", "").replace(".png", "").split("_")
        if len(parts) < 4:
            print(f"⚠️ Skipping invalid filename: {file_name}")
            continue

        base_name = f"{parts[0]}_{parts[1]}"
        region_index = int(parts[3])
        label_path = os.path.join(YOLO_LABEL_FOLDER, f"{base_name}.txt")

        # Get YOLO details
        yolo_info = read_yolo_line_data(label_path, region_index)
        if not yolo_info:
            print(f"⚠️ Skipping {file_name} → index {region_index} not found in YOLO.")
            continue

        # Call classifier API
        encoded = encode_image(image_path)
        response = requests.post(API_URL, json={"image_base64": encoded})

        if response.status_code == 200:
            pred = response.json()
            print(f"📦 API response: {pred}")
            question_number = pred.get("prediction", None)

            results.append({
                "region_index": region_index,
                "filename": file_name,
                "question_number": question_number,
                **yolo_info
            })

            print(f"✅ {file_name} → Q{question_number}")
        else:
            print(f"❌ API error {response.status_code} for {file_name}")

    except Exception as e:
        print(f"❌ Exception while processing {file_name}: {e}")

# === Save results ===
df = pd.DataFrame(results)
df.to_csv(OUTPUT_CSV, index=False)
print(f"\n✅ CSV saved: {OUTPUT_CSV}")
print(df.head())
