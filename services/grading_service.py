import os
import shutil
import pandas as pd

from utils.yolo_runner import run_yolo_on_directory
from utils.cropper import crop_bubbles_and_questions
from utils.model_predictor import predict_bubble_outputs, predict_question_outputs
from utils.ocr_index_numbers import extract_index_numbers
from utils.mapper import map_bubbles_to_questions
from utils.grader import grade_students

# === Paths ===
UPLOAD_DIR = "static/uploaded_sheets"
LABEL_DIR = "static/yolo_labels"
CROPPED_BUBBLE_DIR = "static/cropped_bubbles_to_predict"
CROPPED_QUESTION_DIR = "static/cropped_questions_to_predict"
CROPPED_INDEX_DIR = "static/cropped_index_number"

PREDICTED_BUBBLE_CSV = "backend/predicted_bubbles_with_all_yolo_data.csv"
PREDICTED_QUESTION_CSV = "backend/predicted_question_numbers.csv"
INDEX_PREDICTIONS_CSV = "backend/index_number_predictions_gcv.csv"


def run_grading_pipeline(event_id: str):
    print(f"\n🚀 Starting grading pipeline for event_id: {event_id}\n")

    # === Step 1: Clear temporary folders ===
    for folder in [LABEL_DIR, CROPPED_BUBBLE_DIR, CROPPED_QUESTION_DIR, CROPPED_INDEX_DIR]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
        os.makedirs(folder, exist_ok=True)
        print(f"🧹 Cleared: {folder}")

    # === Step 2: YOLO detection ===
    print("📦 Running YOLO detection...")
    run_yolo_on_directory(UPLOAD_DIR, LABEL_DIR)

    # === Step 3: Crop bubbles, questions, index area ===
    print("✂️ Cropping detected regions...")
    crop_bubbles_and_questions(UPLOAD_DIR, LABEL_DIR, CROPPED_BUBBLE_DIR, CROPPED_QUESTION_DIR, CROPPED_INDEX_DIR)

    # === Step 4: Predict bubble status and numbers ===
    print("🔮 Predicting bubble status and numbers...")
    predict_bubble_outputs(CROPPED_BUBBLE_DIR, LABEL_DIR, PREDICTED_BUBBLE_CSV)

    # === Step 5: Predict question numbers ===
    print("🔢 Predicting question numbers...")
    predict_question_outputs(CROPPED_QUESTION_DIR, LABEL_DIR, PREDICTED_QUESTION_CSV)

    # === Step 6: Predict index number using OCR ===
    print("🔍 Performing OCR for index numbers...")
    extract_index_numbers(CROPPED_INDEX_DIR, INDEX_PREDICTIONS_CSV)

    # === Step 7: Map bubbles to questions ===
    print("🧮 Mapping bubbles to questions...")
    mapped_df = map_bubbles_to_questions(PREDICTED_BUBBLE_CSV, PREDICTED_QUESTION_CSV)
    print("✅ Mapping complete. Sample:")
    print(mapped_df.head())

    # === Step 8: Grade using answer key ===
    print("📝 Running grading logic...")
    final_results = grade_students(event_id, mapped_df, INDEX_PREDICTIONS_CSV)
    print("✅ Grading complete. Sample:")
    print(final_results.head())

    # === Step 9: Save results to CSV ===
    results_dir = "backend/results"
    os.makedirs(results_dir, exist_ok=True)
    FINAL_RESULT_CSV = os.path.join(results_dir, f"{event_id}_final_results.csv")
    final_results.to_csv(FINAL_RESULT_CSV, index=False)
    print(f"📁 Final results saved: {FINAL_RESULT_CSV}\n")

    return FINAL_RESULT_CSV
