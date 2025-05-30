import pandas as pd

# === Load Predicted Matches ===
matches_df = pd.read_csv(r"D:\final year project\backend\top50_question_bubble_matches.csv")

# === Create Mock Answer Key: Q1 → 1, Q2 → 2, ..., Q6 → 1, and so on ===
answer_key = {i: (i % 5) + 1 for i in range(1, 51)}

# === Add Correct Answer Column ===
matches_df["Correct_Answer"] = matches_df["question_number"].map(answer_key)

# === Grade Each Question ===
matches_df["Result"] = matches_df.apply(
    lambda row: "Correct" if row["bubble_number"] == row["Correct_Answer"] else "Wrong",
    axis=1
)

# === Assign Marks: 2 for Correct, 0 for Wrong ===
matches_df["Marks"] = matches_df["Result"].apply(lambda x: 2 if x == "Correct" else 0)

# === Final Score Summary ===
total_questions = len(matches_df)
total_marks = matches_df["Marks"].sum()
max_marks = total_questions * 2
percentage = round((total_marks / max_marks) * 100, 2)

# === Print Summary ===
print(matches_df[["question_number", "bubble_number", "Correct_Answer", "Result", "Marks"]])
print(f"\n🎯 Final Score: {total_marks}/{max_marks} ({percentage}%)")

# === Save to CSV ===
matches_df.to_csv(r"D:\final year project\backend\final_graded_output.csv", index=False)
print("✅ Final graded results saved to: final_graded_output.csv")
