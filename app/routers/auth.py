from fastapi import APIRouter, Depends, HTTPException, Header, UploadFile, File, Request, Response
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
import os
import shutil
from app import models, database
from app.auth import hash_password, verify_password, create_access_token, decode_token
from app.email_utils import send_otp_email
from app.rate_limit import limiter
from app.security import (
    clear_session_cookie,
    get_current_user_id,
    set_csrf_cookie,
    set_session_cookie,
)
import random
import string
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/auth", tags=["auth"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ── Schemas ──────────────────────────────────────────────────────
class CheckEmailRequest(BaseModel):
    email: str

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    otp: str

class SendOTPRequest(BaseModel):
    email: str

class LoginRequest(BaseModel):
    email: str
    password: str

# ── Endpoints ────────────────────────────────────────────────────

@router.post("/check-email")
def check_email(req: CheckEmailRequest, db: Session = Depends(get_db)):
    """Returns whether the email is already registered."""
    user = db.query(models.User).filter(models.User.email == req.email.lower()).first()
    return {"exists": user is not None}


@router.post("/send-otp")
@limiter.limit("5/minute")
def send_otp(req: SendOTPRequest, request: Request, db: Session = Depends(get_db)):
    """Generate and send an OTP to the email address."""
    email = req.email.lower().strip()
    
    # Check if user already exists
    existing = db.query(models.User).filter(models.User.email == email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    # Generate 6-digit OTP
    otp = ''.join(random.choices(string.digits, k=6))
    expires_at = datetime.utcnow() + timedelta(minutes=10)
    
    # Upsert OTP Verification record
    otp_record = db.query(models.OTPVerification).filter(models.OTPVerification.email == email).first()
    if not otp_record:
        otp_record = models.OTPVerification(email=email)
        db.add(otp_record)
        
    otp_record.otp = otp
    otp_record.expires_at = expires_at
    db.commit()
    
    # Send email
    success = send_otp_email(email, otp)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to send OTP email")
        
    return {"message": "OTP sent successfully"}

@router.post("/register")
def register(req: RegisterRequest, response: Response, db: Session = Depends(get_db)):
    """Create a new user account and return a JWT token."""
    email = req.email.lower().strip()
    existing = db.query(models.User).filter(models.User.email == email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    # Validate OTP
    otp_record = db.query(models.OTPVerification).filter(models.OTPVerification.email == email).first()
    if not otp_record:
        raise HTTPException(status_code=400, detail="No OTP requested for this email")
    if otp_record.otp != req.otp.strip():
        raise HTTPException(status_code=400, detail="Invalid OTP")
    if otp_record.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="OTP has expired")

    user = models.User(
        name=req.name.strip(),
        email=email,
        password_hash=hash_password(req.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Clean up OTP record
    db.delete(otp_record)
    db.commit()

    token = create_access_token({"sub": str(user.id), "email": user.email, "name": user.name})
    set_session_cookie(response, token)
    set_csrf_cookie(response)
    return {"token": token, "user": {"id": user.id, "name": user.name, "email": user.email, "profile_pic": user.profile_pic}}


@router.post("/login")
@limiter.limit("10/minute")
def login(req: LoginRequest, request: Request, response: Response, db: Session = Depends(get_db)):
    """Authenticate and return a JWT token."""
    user = db.query(models.User).filter(models.User.email == req.email.lower()).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": str(user.id), "email": user.email, "name": user.name})
    set_session_cookie(response, token)
    set_csrf_cookie(response)
    return {"token": token, "user": {"id": user.id, "name": user.name, "email": user.email, "profile_pic": user.profile_pic}}


@router.get("/me")
def get_me(request: Request, db: Session = Depends(get_db)):
    """Return the currently logged-in user's profile."""
    user_id = get_current_user_id(request)
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": user.id, "name": user.name, "email": user.email, "profile_pic": user.profile_pic,
        "created_at": user.created_at.isoformat() if user.created_at else None
    }


class UpdateProfileRequest(BaseModel):
    name: str

@router.put("/profile")
def update_profile(req: UpdateProfileRequest, request: Request, response: Response, db: Session = Depends(get_db)):
    """Update the logged-in user's display name."""
    user_id = get_current_user_id(request)
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not req.name.strip():
        raise HTTPException(status_code=400, detail="Name cannot be empty")
    user.name = req.name.strip()
    db.commit()
    db.refresh(user)
    # Return a fresh token with the updated name
    new_token = create_access_token({"sub": str(user.id), "email": user.email, "name": user.name})
    set_session_cookie(response, new_token)
    return {"token": new_token, "user": {"id": user.id, "name": user.name, "email": user.email, "profile_pic": user.profile_pic}}

@router.post("/profile/picture")
def upload_profile_picture(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    user_id = get_current_user_id(request)
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    upload_dir = os.path.join(os.path.dirname(__file__), "..", "..", "static", "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    
    file_ext = os.path.splitext(file.filename)[1]
    if not file_ext: file_ext = ".jpg"
    filename = f"user_{user.id}{file_ext}"
    file_path = os.path.join(upload_dir, filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    user.profile_pic = f"uploads/{filename}"
    db.commit()
    db.refresh(user)
    
    return {"message": "Profile picture updated", "profile_pic": user.profile_pic}


@router.post("/logout")
def logout(response: Response):
    clear_session_cookie(response)
    response.delete_cookie("railgo_csrf", path="/")
    return {"message": "Logged out"}
