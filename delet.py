import shutil
import os

# === Paths to delete ===
FOLDERS_TO_DELETE = [
    "static/cropped_bubbles",
    "static/cropped_questions",
    "static/cropped_index"
]

def delete_folders(folder_list):
    for folder in folder_list:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"🗑️ Deleted: {folder}")
        else:
            print(f"⚠️ Folder not found: {folder}")

# === Run it ===
if __name__ == "__main__":
    delete_folders(FOLDERS_TO_DELETE)
