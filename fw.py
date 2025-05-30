import os
import cv2
import numpy as np
import pandas as pd
from PIL import Image, ImageOps

# === Paths ===
IMG_PATH = "static/uploaded_sheets/IMG_3975.JPG"
BUBBLE_CSV = r"D:/final year project/backend/predicted_bubbles_with_all_yolo_data.csv"
QUESTION_CSV = r"D:/final year project/backend/predicted_question_numbers.csv"
OUTPUT_IMAGE = "static/final_mapped_output.jpg"

# === Load and resize image to 640x640 ===
image = Image.open(IMG_PATH).convert("RGB")
image_resized = ImageOps.pad(image, (640, 640), color=(114, 114, 114), centering=(0.5, 0.5))
image_cv2 = cv2.cvtColor(np.array(image_resized), cv2.COLOR_RGB2BGR)

# === Load Data ===
bubbles = pd.read_csv(BUBBLE_CSV)
questions = pd.read_csv(QUESTION_CSV)

# === Prepare question data ===
questions = questions.dropna(subset=["x_center", "y_center", "question_number"])
questions = questions[questions["question_number"].apply(lambda x: str(x).isdigit())]
questions["question_number"] = questions["question_number"].astype(int)
questions["x_px"] = (questions["x_center"] * 640).astype(int)
questions["y_px"] = (questions["y_center"] * 640).astype(int)

# === Draw all question boxes ===
for _, q in questions.iterrows():
    try:
        x1 = int(q["x_center"])
        y1 = int(q["y_center"])
        x2 = int(q["width"])
        y2 = int(q["height"])

        # Clamp
        x1 = max(0, min(x1, 639))
        y1 = max(0, min(y1, 639))
        x2 = max(0, min(x2, 639))
        y2 = max(0, min(y2, 639))

        # Draw blue rectangle for question numbers
        cv2.rectangle(image_cv2, (x1, y1), (x2, y2), (255, 0, 0), 2)
        cv2.putText(image_cv2, f"Q{int(q['question_number'])}", (x1, y1 - 4),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 0, 0), 1)
    except Exception as e:
        print(f"⚠️ Error drawing question box: {e}")

# === Filter top 50 filled bubbles ===
filled = bubbles[bubbles["predicted_filled_status"] == "filled"]
top50 = filled.sort_values(by="filled_probability", ascending=False).head(50)

print("✅ Top 50 filled bubbles:")
print(top50[["filename", "predicted_bubble_number", "filled_probability"]].head())

# === Map and draw top 50 bubbles ===
for _, bubble in top50.iterrows():
    try:
        x1, y1, x2, y2 = int(bubble["x1"]), int(bubble["y1"]), int(bubble["x2"]), int(bubble["y2"])
        bx_center = (x1 + x2) // 2
        by_center = (y1 + y2) // 2

        # Link to nearest question
        questions["distance"] = np.sqrt((questions["x_px"] - bx_center) ** 2 + (questions["y_px"] - by_center) ** 2)
        nearest = questions.sort_values(by="distance").iloc[0]

        q_number = nearest["question_number"]
        q_x = nearest["x_px"]
        q_y = nearest["y_px"]

        # Draw green box for bubble
        cv2.rectangle(image_cv2, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(image_cv2, f"B{int(bubble['predicted_bubble_number'])}", (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        # Mark linked question number with yellow
        cv2.putText(image_cv2, f"Q{int(q_number)}", (q_x, q_y - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        cv2.circle(image_cv2, (q_x, q_y), 4, (0, 255, 255), -1)
    except Exception as e:
        print(f"⚠️ Error mapping bubble: {e}")

# === Save Final Output ===
cv2.imwrite(OUTPUT_IMAGE, image_cv2)
print(f"\n✅ Mapped output saved to: {OUTPUT_IMAGE}")
