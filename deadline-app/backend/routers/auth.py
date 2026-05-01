from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from schemas.user import TokenResponse
from jose import jwt 
from datetime import datetime, timezone, timedelta 
from fastapi.security import OAuth2PasswordRequestForm
import os

router = APIRouter(prefix="/auth", tags=["auth"])

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
EXPIRE_HOURS = int(os.getenv("ACCESS_TOKEN_EXPIRE_HOURS", 8))

def create_token(email: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=EXPIRE_HOURS)
    payload = {
        "sub": email,
        "exp": expire 
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/login", response_model=TokenResponse)
async def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    #1. Find user by email
    user = db.query(User).filter(User.email == form.username).first()

    #2. Check user exists and password is correct
    if not user or not user.verify_password(form.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    #3. Generate token
    token = create_token(user.email)

    #4. Return token
    return TokenResponse(
        access_token=token,
        token_type="bearer"
    )