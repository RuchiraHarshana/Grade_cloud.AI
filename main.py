from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import events, answers, grading, auth, results  # ✅ Now includes results route

app = FastAPI(title="OMR Grading System API")

# === CORS Configuration ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Route Registrations ===
app.include_router(auth.router, prefix="/api", tags=["Authentication"])
app.include_router(events.router, prefix="/api/events", tags=["Events"])
app.include_router(answers.router, prefix="/api/answers", tags=["Answer Keys"])
app.include_router(grading.router, prefix="/api/grading", tags=["Grading"])
app.include_router(results.router, prefix="/api", tags=["Results"])  # ✅ New results route

@app.get("/")
def root():
    return {"message": "OMR Grading API is running"}
