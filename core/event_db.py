# === core/event_db.py ===
import os
import json

DATA_FILE = "data/events.json"
os.makedirs("data", exist_ok=True)

# Load existing events
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        events = json.load(f)
else:
    events = []

def save_event(event):
    events.append(event)
    with open(DATA_FILE, "w") as f:
        json.dump(events, f, indent=2)

def get_events_by_user(user_email: str):
    return [e for e in events if e["user_email"] == user_email]
