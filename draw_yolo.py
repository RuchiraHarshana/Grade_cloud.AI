import os
import cv2
import numpy as np
from PIL import Image, ImageOps

# === Configuration ===
ORIGINAL_IMAGE_PATH = "static/uploaded_sheets/IMG_3975.JPG"
LABEL_PATH = "static/yolo_labels/IMG_3975.txt"
OUTPUT_IMAGE_PATH = "static/IMG_3975_debug.jpg"
YOLO_INPUT_SIZE = 640  # Default YOLO inference size

def resize_with_letterbox(image_path, size=640):
    """Resize image to 640x640 with letterbox padding to preserve aspect ratio"""
    img = Image.open(image_path).convert("RGB")
    img_resized = ImageOps.pad(img, (size, size), color=(114, 114, 114), centering=(0.5, 0.5))
    return np.array(img_resized)

# === Step 1: Resize the original image to 640x640 with padding ===
img = resize_with_letterbox(ORIGINAL_IMAGE_PATH, YOLO_INPUT_SIZE)
img_h, img_w = img.shape[:2]
print(f"🧠 Image resized to {img_w}x{img_h} for YOLO coordinate alignment")

# === Step 2: Load YOLO-predicted labels (x1 y1 x2 y2 pixel coordinates) ===
with open(LABEL_PATH, "r") as f:
    lines = f.readlines()

# === Step 3: Draw bounding boxes ===
for idx, line in enumerate(lines):
    parts = line.strip().split()
    if len(parts) != 5:
        print(f"⚠️ Skipping malformed line {idx}: {line.strip()}")
        continue

    try:
        class_id, x1, y1, x2, y2 = map(float, parts)
        x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])

        # Clamp to 640x640 image boundaries
        x1 = max(0, min(x1, img_w - 1))
        y1 = max(0, min(y1, img_h - 1))
        x2 = max(0, min(x2, img_w - 1))
        y2 = max(0, min(y2, img_h - 1))

        # Draw rectangle and class label
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 1)
        cv2.putText(img, f"Class {int(class_id)}", (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 0, 0), 1)

    except Exception as e:
        print(f"❌ Error at line {idx}: {e}")

# === Step 4: Save debug image ===
os.makedirs(os.path.dirname(OUTPUT_IMAGE_PATH), exist_ok=True)
cv2.imwrite(OUTPUT_IMAGE_PATH, img)
print(f"✅ Saved final debug image: {OUTPUT_IMAGE_PATH}")
