#this used to map filled bubbles with there correspondig question number and save a csv and this is the 7th step
import pandas as pd
import numpy as np

# === Load CSVs ===
bubble_df = pd.read_csv(r"D:\final year project\backend\predicted_bubbles_with_all_yolo_data.csv")
question_df = pd.read_csv(r"D:\final year project\backend\predicted_question_numbers.csv")

# === Filter Top 50 Filled Bubbles ===
filled_bubbles = bubble_df[bubble_df["predicted_filled_status"] == "filled"]
top50 = filled_bubbles.sort_values(by="filled_probability", ascending=False).head(50).copy()

# === Compute Bubble Centers ===
top50["x_center_px"] = ((top50["x1"] + top50["x2"]) / 2).astype(float)
top50["y_center_px"] = ((top50["y1"] + top50["y2"]) / 2).astype(float)

# === Compute Question Centers ===
question_df["x_center_px"] = question_df["x_center"].astype(float)
question_df["y_center_px"] = question_df["y_center"].astype(float)

# === Matching Logic ===
angle_tolerance_deg = 18
angle_tolerance_rad = np.deg2rad(angle_tolerance_deg)
matches = []

def angle_with_horizontal(vec):
    horizontal = np.array([1, 0])
    unit_vec = vec / np.linalg.norm(vec) if np.linalg.norm(vec) != 0 else vec
    dot_product = np.clip(np.dot(unit_vec, horizontal), -1.0, 1.0)
    return np.arccos(dot_product)

for i, q_row in question_df.iterrows():
    q_point = np.array([q_row["x_center_px"], q_row["y_center_px"]])
    candidates = []

    for j, b_row in top50.iterrows():
        b_point = np.array([b_row["x_center_px"], b_row["y_center_px"]])
        if b_point[0] > q_point[0]:  # bubble must be to the right
            angle = angle_with_horizontal(b_point - q_point)
            if angle <= angle_tolerance_rad:
                dist = np.linalg.norm(q_point - b_point)
                candidates.append((j, dist))

    if candidates:
        best_idx, best_dist = min(candidates, key=lambda x: x[1])
        matched_bubble = top50.loc[best_idx]

        matches.append({
            "question_number": int(q_row["question_number"]),
            "bubble_number": int(matched_bubble["predicted_bubble_number"]),
            "bubble_index": int(matched_bubble["region_index"]),
            "bubble_confidence": round(matched_bubble["filled_probability"], 6),
            "distance": round(best_dist, 2)
        })
    else:
        matches.append({
            "question_number": int(q_row["question_number"]),
            "bubble_number": None,
            "bubble_index": None,
            "bubble_confidence": None,
            "distance": None
        })

# === Final Matched DataFrame ===
matched_df = pd.DataFrame(matches)

# ✅ Sort by question_number
matched_df.sort_values(by="question_number", inplace=True)

# ✅ Print nicely
print("\n✅ Mapped Bubble ↔ Question Matches (Sorted by Question):")
print(matched_df.reset_index(drop=True))

# ✅ Save to CSV
output_path = r"D:\final year project\backend\top50_question_bubble_matches.csv"
matched_df.to_csv(output_path, index=False)
print(f"\n📁 Saved matched data to: {output_path}")
