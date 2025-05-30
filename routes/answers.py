# === Updated routes/answer_key.py ===

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import os
import json

router = APIRouter()

ANSWER_KEY_DIR = "backend/answer_keys"
os.makedirs(ANSWER_KEY_DIR, exist_ok=True)

class AnswerItem(BaseModel):
    question_number: int
    correct_bubble_number: int

class AnswerKeyRequest(BaseModel):
    event_id: str
    answers: List[AnswerItem]
    mark_per_question: float

@router.post("/submit-answer-key")
def submit_answer_key(data: AnswerKeyRequest):
    if not data.event_id:
        raise HTTPException(status_code=400, detail="Missing event_id.")

    # Convert to dict
    answer_dict = {
        "answer_key": {str(item.question_number): item.correct_bubble_number for item in data.answers},
        "mark_per_question": data.mark_per_question
    }

    # Save as JSON file
    json_path = os.path.join(ANSWER_KEY_DIR, f"{data.event_id}.json")
    try:
        with open(json_path, "w") as f:
            json.dump(answer_dict, f, indent=2)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save answer key: {e}")

    return {
        "status": "success",
        "event_id": data.event_id,
        "total_questions": len(data.answers),
        "file_saved": json_path
    }
