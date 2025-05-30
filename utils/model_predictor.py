import os
import base64
import requests
import pandas as pd

# === Model API Endpoints ===
BUBBLE_API = "https://bubble-classifier-service-744417252774.us-central1.run.app/predict"
FILLED_API = "https://filled-classifier-service-744417252774.us-central1.run.app/predict"
QUESTION_API = "https://question-classifier-service-744417252774.us-central1.run.app/predict"

# === Helper to Encode Image to base64 ===
def encode_image_base64(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

# === Individual Predictors ===
def predict_filled(image_path):
    encoded = encode_image_base64(image_path)
    try:
        response = requests.post(FILLED_API, json={"image_base64": encoded})
        result = response.json()
        return result.get("prediction"), result.get("confidence")
    except Exception as e:
        print(f"❌ Filled prediction failed: {e}")
        return None, None

def predict_bubble_number(image_path):
    encoded = encode_image_base64(image_path)
    try:
        response = requests.post(BUBBLE_API, json={"image_base64": encoded})
        result = response.json()
        return result.get("prediction")
    except Exception as e:
        print(f"❌ Bubble number prediction failed: {e}")
        return None

def predict_question_number(image_path):
    encoded = encode_image_base64(image_path)
    try:
        response = requests.post(QUESTION_API, json={"image_base64": encoded})
        result = response.json()
        return result.get("prediction")
    except Exception as e:
        print(f"❌ Question number prediction failed: {e}")
        return None

# === New: Bulk Bubble Prediction Pipeline ===
def predict_bubble_outputs(bubble_dir, label_dir, output_csv_path):
    results = []

    for fname in sorted(os.listdir(bubble_dir)):
        if not fname.lower().endswith((".jpg", ".jpeg", ".png")):
            continue

        path = os.path.join(bubble_dir, fname)
        try:
            parts = fname.replace(".jpg", "").replace(".jpeg", "").replace(".png", "").split("_")
            base = f"{parts[0]}_{parts[1]}"
            class_id = int(parts[2])
            region_index = int(parts[3])

            if class_id != 0:
                continue

            label_path = os.path.join(label_dir, f"{base}.txt")
            if not os.path.exists(label_path):
                continue

            with open(label_path) as f:
                lines = f.readlines()
                if region_index >= len(lines):
                    continue
                x1, y1, x2, y2 = map(int, map(float, lines[region_index].strip().split()[1:]))

            filled_pred, filled_conf = predict_filled(path)
            bubble_num = predict_bubble_number(path)

            results.append({
                "region_index": region_index,
                "filename": fname,
                "predicted_bubble_number": bubble_num,
                "predicted_filled_status": filled_pred,
                "filled_probability": filled_conf,
                "class_id": class_id,
                "x1": x1, "y1": y1, "x2": x2, "y2": y2
            })

        except Exception as e:
            print(f"❌ Error in {fname}: {e}")

    df = pd.DataFrame(results)
    df.to_csv(output_csv_path, index=False)
    print(f"✅ Bubble predictions saved: {output_csv_path}")


# === New: Bulk Question Number Prediction Pipeline ===
def predict_question_outputs(question_dir, label_dir, output_csv_path):
    results = []

    for fname in sorted(os.listdir(question_dir)):
        if not fname.lower().endswith((".jpg", ".jpeg", ".png")):
            continue

        path = os.path.join(question_dir, fname)

        try:
            parts = fname.replace(".jpg", "").replace(".jpeg", "").replace(".png", "").split("_")
            base = f"{parts[0]}_{parts[1]}"
            region_index = int(parts[3])
            label_path = os.path.join(label_dir, f"{base}.txt")

            if not os.path.exists(label_path):
                continue

            with open(label_path) as f:
                lines = f.readlines()
                count = -1
                for i, line in enumerate(lines):
                    if int(float(line.strip().split()[0])) == 1:
                        count += 1
                    if count == region_index:
                        x_center, y_center, width, height = map(float, line.strip().split()[1:])
                        break
                else:
                    continue  # not found

            q_number = predict_question_number(path)

            results.append({
                "region_index": region_index,
                "filename": fname,
                "question_number": q_number,
                "x_center": round(x_center, 6),
                "y_center": round(y_center, 6),
                "width": round(width, 6),
                "height": round(height, 6)
            })

        except Exception as e:
            print(f"❌ Error in {fname}: {e}")

    df = pd.DataFrame(results)
    df.to_csv(output_csv_path, index=False)
    print(f"✅ Question predictions saved: {output_csv_path}")
