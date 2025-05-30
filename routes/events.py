from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from uuid import uuid4
import datetime
from core import event_db  # ✅ Using our new file-based DB

router = APIRouter()

class EventRequest(BaseModel):
    module_code: str
    module_name: str
    description: str
    user_email: str

@router.post("/create-event")
def create_event(event: EventRequest):
    event_id = str(uuid4())
    timestamp = datetime.datetime.utcnow().isoformat()

    event_data = {
        "event_id": event_id,
        "module_code": event.module_code,
        "module_name": event.module_name,
        "description": event.description,
        "created_at": timestamp,
        "user_email": event.user_email,
    }

    event_db.save_event(event_data)
    return {"status": "success", "event_id": event_id, "event_data": event_data}

@router.get("/")
def get_events(user_email: str = Query(...)):
    return event_db.get_events_by_user(user_email)
