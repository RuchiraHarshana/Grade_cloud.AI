import os
import io
import pandas as pd
from google.cloud import vision
from google.oauth2 import service_account

# Update this to the actual path of your credentials JSON
CREDENTIAL_PATH = "D:/final year project/backend/bigdata-454518-47ddac2ef18a.json"

# Initialize the Vision API client
credentials = service_account.Credentials.from_service_account_file(CREDENTIAL_PATH)
client = vision.ImageAnnotatorClient(credentials=credentials)

def extract_index_numbers(index_folder: str, output_csv: str):
    """Extract index numbers from cropped images and save to CSV."""
    results = []

    for fname in sorted(os.listdir(index_folder)):
        if fname.lower().endswith((".jpg", ".jpeg", ".png")):
            img_path = os.path.join(index_folder, fname)
            with io.open(img_path, "rb") as f:
                content = f.read()

            image = vision.Image(content=content)
            response = client.text_detection(image=image)
            texts = response.text_annotations

            if texts:
                extracted = texts[0].description.strip().replace("\n", "")
            else:
                extracted = "UNKNOWN"

            results.append({"filename": fname, "index_number": extracted})
            print(f"📄 {fname} → {extracted}")

    # Save results
    df = pd.DataFrame(results)
    df.to_csv(output_csv, index=False)
    print(f"✅ OCR results saved to: {output_csv}")
