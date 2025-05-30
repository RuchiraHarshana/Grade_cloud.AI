from fastapi import APIRouter, HTTPException
import os
import pandas as pd

router = APIRouter()

@router.get("/results/{event_id}")
def get_results(event_id: str):
    path = f"backend/results/{event_id}_final_results.csv"
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Results not found")

    try:
        df = pd.read_csv(path)
        return {"results": df.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read results CSV: {e}")
