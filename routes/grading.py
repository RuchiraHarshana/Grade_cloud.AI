from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import List
import os
import shutil
from services.grading_service import run_grading_pipeline

router = APIRouter()

UPLOAD_DIR = "static/uploaded_sheets"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload-sheets")
async def upload_omr_sheets(
    event_id: str = Form(...),
    files: List[UploadFile] = File(...)
):
    try:
        saved_files = []
        for file in files:
            save_path = os.path.join(UPLOAD_DIR, file.filename)
            with open(save_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            saved_files.append(save_path)

        return {
            "status": "success",
            "event_id": event_id,
            "uploaded_files": saved_files
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {e}")


# ✅ Updated grading endpoint
class GradeRequest(BaseModel):
    event_id: str

@router.post("/grade-papers")
def grade_event(data: GradeRequest):
    try:
        result_csv_path = run_grading_pipeline(data.event_id)
        return {"message": "Grading complete", "result_file": result_csv_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
