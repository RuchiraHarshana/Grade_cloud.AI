import pandas as pd
import numpy as np

def map_bubbles_to_questions(bubble_csv, question_csv):
    bubbles = pd.read_csv(bubble_csv)
    questions = pd.read_csv(question_csv)

    filled = bubbles[bubbles["predicted_filled_status"] == "filled"]
    top50 = filled.sort_values(by="filled_probability", ascending=False).head(50).copy()

    top50["x_center_px"] = ((top50["x1"] + top50["x2"]) / 2).astype(float)
    top50["y_center_px"] = ((top50["y1"] + top50["y2"]) / 2).astype(float)
    questions["x_center_px"] = questions["x_center"].astype(float)
    questions["y_center_px"] = questions["y_center"].astype(float)

    def angle_with_horizontal(vec):
        horizontal = np.array([1, 0])
        unit_vec = vec / np.linalg.norm(vec) if np.linalg.norm(vec) != 0 else vec
        return np.arccos(np.clip(np.dot(unit_vec, horizontal), -1.0, 1.0))

    angle_tolerance_rad = np.deg2rad(18)
    matches = []

    for _, q_row in questions.iterrows():
        q = np.array([q_row["x_center_px"], q_row["y_center_px"]])
        candidates = []

        for _, b_row in top50.iterrows():
            b = np.array([b_row["x_center_px"], b_row["y_center_px"]])
            if b[0] > q[0]:
                angle = angle_with_horizontal(b - q)
                if angle <= angle_tolerance_rad:
                    dist = np.linalg.norm(b - q)
                    candidates.append((b_row, dist))

        if candidates:
            best, dist = min(candidates, key=lambda x: x[1])
            matches.append({
                "question_number": int(q_row["question_number"]),
                "bubble_number": int(best["predicted_bubble_number"]),
                "bubble_index": int(best["region_index"]),
                "bubble_confidence": round(best["filled_probability"], 6),
                "distance": round(dist, 2)
            })
        else:
            matches.append({
                "question_number": int(q_row["question_number"]),
                "bubble_number": None,
                "bubble_index": None,
                "bubble_confidence": None,
                "distance": None
            })

    return pd.DataFrame(matches)
