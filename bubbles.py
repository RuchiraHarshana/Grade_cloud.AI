#this is used to pass bubbles from the directory to to model end points and get prediction and get a output csv this is step 3
import os
import base64
import requests
import pandas as pd

# === CONFIG ===
LABEL_FOLDER = r"D:\final year project\backend\static\yolo_labels"
BUBBLE_FOLDER = r"D:\final year project\backend\static\cropped_bubbles_to_predict"
OUTPUT_CSV = r"D:\final year project\backend\predicted_bubbles_with_all_yolo_data.csv"

FILLED_API_URL = "https://filled-classifier-service-744417252774.us-central1.run.app/predict"
BUBBLE_API_URL = "https://bubble-classifier-service-744417252774.us-central1.run.app/predict"

# === Helper: Encode image as base64 ===
def encode_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

# === Helper: Call APIs for predictions ===
def predict_filled_and_bubble(image_path):
    encoded = encode_image(image_path)

    filled_resp = requests.post(FILLED_API_URL, json={"image_base64": encoded})
    bubble_resp = requests.post(BUBBLE_API_URL, json={"image_base64": encoded})

    filled = filled_resp.json() if filled_resp.ok else {}
    bubble = bubble_resp.json() if bubble_resp.ok else {}

    filled_prediction = filled.get("prediction")           # "filled" or "unfilled"
    filled_confidence = filled.get("confidence")           # float
    bubble_number = bubble.get("prediction")               # int (1–5)

    return filled_prediction, filled_confidence, bubble_number

# === Helper: Read YOLO label data (absolute coords) ===
def load_absolute_yolo_labels(label_file):
    labels = []
    with open(label_file, "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 5:
                labels.append({
                    "class_id": int(float(parts[0])),
                    "x1": int(float(parts[1])),
                    "y1": int(float(parts[2])),
                    "x2": int(float(parts[3])),
                    "y2": int(float(parts[4]))
                })
    return labels

# === Main: Process all cropped bubble images ===
results = []

bubble_images = sorted([
    f for f in os.listdir(BUBBLE_FOLDER)
    if f.lower().endswith((".jpg", ".png"))
])

for bubble_image in bubble_images:
    try:
        # Parse filename: IMG_3975_0_42.jpg
        parts = bubble_image.replace(".jpg", "").replace(".png", "").split("_")
        if len(parts) < 4:
            print(f"⚠️ Skipping invalid filename: {bubble_image}")
            continue

        base_name = f"{parts[0]}_{parts[1]}"  # e.g., IMG_3975
        class_id = int(parts[2])
        region_index = int(parts[3])

        if class_id != 0:
            continue  # Skip non-bubble crops

        label_path = os.path.join(LABEL_FOLDER, f"{base_name}.txt")
        bubble_path = os.path.join(BUBBLE_FOLDER, bubble_image)

        if not os.path.exists(label_path):
            print(f"⚠️ Missing label file for {bubble_image}")
            continue

        labels = load_absolute_yolo_labels(label_path)
        if region_index >= len(labels):
            print(f"⚠️ Index out of bounds for {bubble_image}")
            continue

        label = labels[region_index]
        if label["class_id"] != 0:
            print(f"⚠️ YOLO class mismatch in {bubble_image}")
            continue

        # Predict via API
        filled_pred, filled_prob, bubble_pred = predict_filled_and_bubble(bubble_path)

        # Collect result
        results.append({
            "region_index": region_index,
            "filename": bubble_image,
            "predicted_bubble_number": bubble_pred,
            "predicted_filled_status": filled_pred,
            "filled_probability": filled_prob,
            "class_id": label["class_id"],
            "x1": label["x1"],
            "y1": label["y1"],
            "x2": label["x2"],
            "y2": label["y2"]
        })

    except Exception as e:
        print(f"❌ Error processing {bubble_image}: {e}")

# === Save all results to CSV ===
df = pd.DataFrame(results)
df.to_csv(OUTPUT_CSV, index=False)
print(f"\n✅ Saved predictions to: {OUTPUT_CSV}")
print(df.head())
