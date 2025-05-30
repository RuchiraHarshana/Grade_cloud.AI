#this is used to crop question numbers correctly nd stroes them in folder this is step 4
import os
import cv2
import shutil
import numpy as np
from PIL import Image, ImageOps

# === CONFIG ===
IMAGE_FOLDER = "static/uploaded_sheets"
LABEL_FOLDER = "static/yolo_labels"
OUTPUT_FOLDER = "D:/final year project/backend/static/cropped_questions_to_predict"
YOLO_INPUT_SIZE = (640, 640)

def clear_output_folder(folder_path):
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
    os.makedirs(folder_path, exist_ok=True)
    print(f"🧹 Cleared and created: {folder_path}")

def resize_to_yolo_format(image_path, target_size=(640, 640)):
    img = Image.open(image_path).convert("RGB")
    padded = ImageOps.pad(img, target_size, color=(114, 114, 114), centering=(0.5, 0.5))
    return np.array(padded), os.path.splitext(os.path.basename(image_path))[0]

def crop_question_regions(resized_image, label_path, output_folder, base_name):
    img_h, img_w = resized_image.shape[:2]
    count = 0

    if not os.path.exists(label_path):
        print(f"⚠️ Label file not found for {base_name}")
        return

    with open(label_path, "r") as f:
        lines = f.readlines()

    for idx, line in enumerate(lines):
        parts = line.strip().split()
        if len(parts) != 5:
            continue

        try:
            class_id = int(float(parts[0]))
            if class_id != 1:
                continue

            x1, y1, x2, y2 = map(int, map(float, parts[1:]))

            # Clamp to bounds
            x1 = max(0, min(x1, img_w - 1))
            y1 = max(0, min(y1, img_h - 1))
            x2 = max(0, min(x2, img_w - 1))
            y2 = max(0, min(y2, img_h - 1))

            if x2 <= x1 or y2 <= y1:
                print(f"⚠️ Skipping invalid crop at line {idx}")
                continue

            cropped = resized_image[y1:y2, x1:x2]
            if cropped.size == 0:
                print(f"⚠️ Empty crop at line {idx}")
                continue

            save_path = os.path.join(output_folder, f"{base_name}_1_{count}.jpg")
            cv2.imwrite(save_path, cropped)
            print(f"[✓] Saved: {save_path}")
            count += 1

        except Exception as e:
            print(f"❌ Error at line {idx}: {e}")

    print(f"✅ Total class 1 (question number) crops saved for {base_name}: {count}")

# === MAIN LOOP ===
if __name__ == "__main__":
    clear_output_folder(OUTPUT_FOLDER)

    for fname in os.listdir(IMAGE_FOLDER):
        if fname.lower().endswith((".jpg", ".jpeg", ".png")):
            image_path = os.path.join(IMAGE_FOLDER, fname)
            base_name = os.path.splitext(fname)[0]
            label_path = os.path.join(LABEL_FOLDER, base_name + ".txt")

            resized_img, _ = resize_to_yolo_format(image_path, YOLO_INPUT_SIZE)
            crop_question_regions(resized_img, label_path, OUTPUT_FOLDER, base_name)
