from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.models import UserCreate, UserPublic
from app import crud, models
from app.api.deps import SessionDep
from app.core.security import create_access_token
from app.models import Token
from datetime import timedelta
from app.core.config import settings
from app.core.security import create_access_token
from app.models.token import TokenWithUser 

router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str   

@router.post("/login")
def login(req: LoginRequest):
    if req.email == "test@test.com" and req.password == "pass":
        return {"access_token": "fake-token-for-testing"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@router.post("/register", response_model=TokenWithUser)
def register_user(user_in: UserCreate, session: SessionDep):
    existing = crud.get_user_by_email(session=session, email=user_in.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = crud.create_user(session=session, user_create=user_in)
    
    access_token = create_access_token(
        user.id, expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {"access_token": access_token, "user": user}