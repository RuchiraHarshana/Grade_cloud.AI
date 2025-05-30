#this is used to get cropped images from the path and get the index number using cloud vision and save it in a csv
import os
from google.cloud import vision
from google.oauth2 import service_account
from PIL import Image
import io

# === PATH TO YOUR CREDENTIAL FILE ===
key_path = "/content/bigdata-454518-47ddac2ef18a.json"  # ✅ Make sure your key file is here

# === Initialize the Vision API Client ===
credentials = service_account.Credentials.from_service_account_file(key_path)
client = vision.ImageAnnotatorClient(credentials=credentials)

# === Directory with cropped index images ===
image_folder = "D:\final year project\backend\static\cropped_index_number"
output_text = []

# === Process only first 4 images ===
image_files = sorted([f for f in os.listdir(image_folder) if f.endswith(('.jpg', '.png'))])[:4]

for filename in image_files:
    file_path = os.path.join(image_folder, filename)

    with io.open(file_path, "rb") as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    # OCR request
    response = client.text_detection(image=image)
    texts = response.text_annotations

    if texts:
        detected_text = texts[0].description.strip().replace("\n", "")
    else:
        detected_text = "No text found"

    print(f"{filename}: {detected_text}")
    output_text.append({'filename': filename, 'index_number': detected_text})

# === (Optional) Save to CSV ===
import pandas as pd
df = pd.DataFrame(output_text)
df.to_csv("D:/final year project/backend/index_number_predictions_gcv.csv", index=False)
print("✅ Extracted text saved to CSV.")
