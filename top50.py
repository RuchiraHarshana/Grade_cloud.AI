import pandas as pd

# === Load the original predictions CSV ===
CSV_PATH = r"D:\final year project\backend\predicted_bubbles_with_all_yolo_data.csv"
df = pd.read_csv(CSV_PATH)

# === Step 1: Filter only 'filled' bubbles ===
filled_df = df[df["predicted_filled_status"] == "filled"]

# === Step 2: Sort by 'filled_probability' in descending order ===
sorted_df = filled_df.sort_values(by="filled_probability", ascending=False)

# === Step 3: Select the top 50 entries ===
top_50_filled_df = sorted_df.head(50)

# ✅ Now the DataFrame is ready in memory:
print("✅ Top 50 filled bubbles (as DataFrame):")
print(top_50_filled_df.head())

# You can now use `top_50_filled_df` in further logic
