from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from uuid import uuid4

router = APIRouter()

# 🧪 Simulated in-memory database
fake_users_db = {
    "teacher1@example.com": {
        "email": "teacher1@example.com",
        "password": "password123",  # 🔐 Use hashed passwords in production!
        "user_id": str(uuid4())
    },
    "teacher2@example.com": {
        "email": "teacher2@example.com",
        "password": "secret456",
        "user_id": str(uuid4())
    }
}

# 📨 Request model
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# 🔐 Auth endpoint
@router.post("/login")
def login_user(data: LoginRequest):
    user = fake_users_db.get(data.email)

    if not user or user["password"] != data.password:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {
        "status": "success",
        "user_id": user["user_id"],
        "email": user["email"]
    }
