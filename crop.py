#this used to get yolo labels and crop bubbles and index  this is step 2

import os
import cv2
import shutil
from PIL import Image, ImageOps
import numpy as np

# === CONFIG ===
IMAGE_FOLDER = "static/uploaded_sheets"
LABEL_FOLDER = "static/yolo_labels"
YOLO_INPUT_SIZE = 640

# Output only for class 0 (bubbles) and class 2 (index number)
OUTPUT_DIRS = {
    0: "D:/final year project/backend/static/cropped_bubbles_to_predict",
    2: "D:/final year project/backend/static/cropped_index_number"
}

def clear_output_dirs(dirs: dict):
    for dir_path in dirs.values():
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
        os.makedirs(dir_path, exist_ok=True)
        print(f"🧹 Cleared: {dir_path}")

def resize_with_letterbox(image_path, size=640):
    img = Image.open(image_path).convert("RGB")
    padded = ImageOps.pad(img, (size, size), color=(114, 114, 114), centering=(0.5, 0.5))
    return np.array(padded), os.path.splitext(os.path.basename(image_path))[0]

def crop_absolute_bboxes(resized_img, label_path, output_dirs, base_name):
    img_h, img_w = resized_img.shape[:2]

    if not os.path.exists(label_path):
        print(f"⚠️ No label file for {base_name}")
        return

    with open(label_path, 'r') as f:
        lines = f.readlines()

    for idx, line in enumerate(lines):
        parts = line.strip().split()
        if len(parts) != 5:
            print(f"⚠️ Skipping malformed line {idx}: {line.strip()}")
            continue

        try:
            class_id, x1, y1, x2, y2 = map(int, map(float, parts))
            if class_id not in output_dirs:
                continue

            # Clamp to bounds
            x1 = max(0, min(x1, img_w - 1))
            y1 = max(0, min(y1, img_h - 1))
            x2 = max(0, min(x2, img_w - 1))
            y2 = max(0, min(y2, img_h - 1))

            if x2 <= x1 or y2 <= y1:
                print(f"⚠️ Skipping zero-area crop at line {idx}")
                continue

            crop = resized_img[y1:y2, x1:x2]
            if crop.size == 0:
                print(f"⚠️ Empty crop at line {idx}")
                continue

            save_path = os.path.join(output_dirs[class_id], f"{base_name}_{class_id}_{idx}.jpg")
            cv2.imwrite(save_path, crop)
            print(f"[✓] Saved: {save_path}")

        except Exception as e:
            print(f"❌ Error at line {idx}: {e}")

# === MAIN LOOP ===
if __name__ == "__main__":
    clear_output_dirs(OUTPUT_DIRS)

    for fname in os.listdir(IMAGE_FOLDER):
        if fname.lower().endswith((".jpg", ".jpeg", ".png")):
            image_path = os.path.join(IMAGE_FOLDER, fname)
            label_name = os.path.splitext(fname)[0] + ".txt"
            label_path = os.path.join(LABEL_FOLDER, label_name)

            resized_image, base_name = resize_with_letterbox(image_path, YOLO_INPUT_SIZE)
            crop_absolute_bboxes(resized_image, label_path, OUTPUT_DIRS, base_name)
