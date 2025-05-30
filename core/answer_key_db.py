# === core/answer_key_db.py ===

import os
import json

ANSWER_KEY_DIR = "backend/answer_keys"

def get_answer_key(event_id: str):
    """
    Load the answer key for a given event ID from its JSON file.
    Returns:
        - answer_key: dict (question_number → correct_bubble_number)
        - mark_per_question: float
    Raises:
        - FileNotFoundError if event does not exist
        - ValueError if file is malformed
    """
    file_path = os.path.join(ANSWER_KEY_DIR, f"{event_id}.json")
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"No answer key found for event_id: {event_id}")

    try:
        with open(file_path, "r") as f:
            data = json.load(f)

        answer_key = data.get("answer_key", {})
        mark_per_question = data.get("mark_per_question", 1.0)

        return answer_key, mark_per_question

    except Exception as e:
        raise ValueError(f"Failed to load answer key for event_id {event_id}: {e}")
