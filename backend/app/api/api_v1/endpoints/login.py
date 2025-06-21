from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str
    is_verified: bool = False

@router.post("/login")
def login(request: LoginRequest):
    if not request.is_verified:
        raise HTTPException(status_code=403, detail="Email not verified")
    return {"message": f"Welcome {request.email}"}
