# ✅ utils/grader.py (BACKEND)
import os
import pandas as pd
from core.answer_key_db import get_answer_key

def grade_students(event_id, matched_df, index_csv_path):
    print("\U0001F4E5 Grading started...")

    # === 1. Try to read index number ===
    index_number = "UNKNOWN"
    try:
        if os.path.exists(index_csv_path) and os.path.getsize(index_csv_path) > 0:
            index_df = pd.read_csv(index_csv_path)
            if not index_df.empty and "index_number" in index_df.columns:
                value = str(index_df.iloc[0]["index_number"]).strip()
                if value:
                    index_number = value
    except Exception as e:
        print(f"\u26A0\ufe0f Could not read index number CSV: {e}")

    # === 2. Load answer key ===
    try:
        answer_key, mark_per_question = get_answer_key(event_id)
        print(f"\U0001F4D8 Loaded answer key with {len(answer_key)} entries. Mark per question: {mark_per_question}")
    except Exception as e:
        raise ValueError(f"\u274C Failed to load answer key: {e}")

    # === 3. Check if matched_df is empty ===
    if matched_df.empty:
        print("\u274C Matched dataframe is empty — nothing to grade.")
        return pd.DataFrame([{
            "index_number": index_number,
            "correct_answers": 0,
            "score": 0,
            "total": len(answer_key) * mark_per_question
        }])

    # === 4. Grade each question ===
    matched_df["is_correct"] = matched_df.apply(
        lambda row: answer_key.get(str(int(row["question_number"]))) == int(row["bubble_number"])
        if pd.notnull(row["bubble_number"]) else False,
        axis=1
    )

    matched_df["score"] = matched_df["is_correct"].astype(int) * mark_per_question

    # === 5. Calculate total score and correct ===
    total_score = matched_df["score"].sum()
    correct_count = matched_df["is_correct"].sum()
    total_marks = len(answer_key) * mark_per_question

    # === 6. Return summary only ===
    summary_df = pd.DataFrame([{
        "index_number": index_number,
        "correct_answers": int(correct_count),
        "score": total_score,
        "total": total_marks
    }])

    print(f"\u2705 Final grade for {index_number}: {total_score}")
    return summary_df
