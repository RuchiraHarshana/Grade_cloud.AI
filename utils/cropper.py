'''Takes a YOLO label file + resized image

Crops regions by class (0, 1, 2)

Saves each cropped image into its appropriate folder'''

import os
import cv2
import shutil
import numpy as np
from PIL import Image, ImageOps

YOLO_INPUT_SIZE = 640

# Output folders per class
CROP_OUTPUT_DIRS = {
    0: "static/cropped_bubbles_to_predict",
    1: "static/cropped_questions_to_predict",
    2: "static/cropped_index_number"
}


def clear_crop_folders():
    """Clear and recreate cropped image folders."""
    for path in CROP_OUTPUT_DIRS.values():
        if os.path.exists(path):
            shutil.rmtree(path)
        os.makedirs(path, exist_ok=True)
        print(f"🧹 Cleared: {path}")


def resize_with_letterbox(image_path, size=640):
    """Resize to YOLO input size with letterbox padding"""
    img = Image.open(image_path).convert("RGB")
    padded = ImageOps.pad(img, (size, size), color=(114, 114, 114), centering=(0.5, 0.5))
    return np.array(padded), os.path.splitext(os.path.basename(image_path))[0]


def crop_yolo_labels(image_array, label_path, base_name):
    """Crop regions from image using YOLO-format pixel coords."""
    h, w = image_array.shape[:2]

    with open(label_path, "r") as f:
        lines = f.readlines()

    class_counts = {0: 0, 1: 0, 2: 0}

    for idx, line in enumerate(lines):
        try:
            parts = line.strip().split()
            if len(parts) != 5:
                continue
            class_id, x1, y1, x2, y2 = map(int, map(float, parts))
            if class_id not in CROP_OUTPUT_DIRS:
                continue

            # Clamp box to image bounds
            x1 = max(0, min(x1, w - 1))
            y1 = max(0, min(y1, h - 1))
            x2 = max(0, min(x2, w - 1))
            y2 = max(0, min(y2, h - 1))

            if x2 <= x1 or y2 <= y1:
                continue

            crop = image_array[y1:y2, x1:x2]
            if crop.size == 0:
                continue

            out_path = os.path.join(
                CROP_OUTPUT_DIRS[class_id],
                f"{base_name}_{class_id}_{class_counts[class_id]}.jpg"
            )
            cv2.imwrite(out_path, crop)
            class_counts[class_id] += 1

        except Exception as e:
            print(f"❌ Error in line {idx}: {e}")

    print(f"✅ Crops saved for: {base_name}")


# ✅ NEW FUNCTION — This is what grading_service.py expects
def crop_bubbles_and_questions(image_dir, label_dir, bubble_output_dir, question_output_dir, index_output_dir):
    """Wrapper to process all images and crop bubbles, questions, and index."""
    # Use your defined output folders
    CROP_OUTPUT_DIRS[0] = bubble_output_dir
    CROP_OUTPUT_DIRS[1] = question_output_dir
    CROP_OUTPUT_DIRS[2] = index_output_dir

    clear_crop_folders()

    for fname in os.listdir(image_dir):
        if fname.lower().endswith((".jpg", ".jpeg", ".png")):
            image_path = os.path.join(image_dir, fname)
            label_path = os.path.join(label_dir, os.path.splitext(fname)[0] + ".txt")

            if not os.path.exists(label_path):
                print(f"⚠️ No label found for: {fname}")
                continue

            resized_image, base_name = resize_with_letterbox(image_path, YOLO_INPUT_SIZE)
            crop_yolo_labels(resized_image, label_path, base_name)
