from fastapi import APIRouter, Depends, HTTPException, Header, UploadFile, File, Request, Response
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
import os
import shutil
import io
from app import models, database
from app.auth import hash_password, verify_password, create_access_token, decode_token
from app.email_utils import send_otp_email, send_forgot_password_email
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

# ── Allowed image magic bytes ─────────────────────────────────────────────────
_ALLOWED_IMAGES = {
    b'\xff\xd8\xff': ('jpeg', '.jpg'),
    b'\x89PNG\r\n\x1a\n': ('png', '.png'),
    b'GIF87a': ('gif', '.gif'),
    b'GIF89a': ('gif', '.gif'),
}
MAX_UPLOAD_BYTES = 5 * 1024 * 1024  # 5 MB

def _detect_image(header: bytes):
    """Return (mime_type, extension) if header matches a known image, else None."""
    for magic, info in _ALLOWED_IMAGES.items():
        if header.startswith(magic):
            return info
    # WebP: RIFF????WEBP
    if len(header) >= 12 and header[:4] == b'RIFF' and header[8:12] == b'WEBP':
        return ('webp', '.webp')
    return None

@router.post("/profile/picture")
async def upload_profile_picture(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    user_id = get_current_user_id(request)
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # ── Read entire file into memory so we can validate it ────────────────────
    contents = await file.read()

    # 1. Enforce file size limit
    if len(contents) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 5 MB.")

    # 2. Validate MIME type via magic bytes (not just file extension)
    image_info = _detect_image(contents[:12])
    if image_info is None:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only JPEG, PNG, GIF, and WebP images are allowed."
        )
    _, safe_ext = image_info

    upload_dir = os.path.join(os.path.dirname(__file__), "..", "..", "static", "uploads")
    os.makedirs(upload_dir, exist_ok=True)

    filename = f"user_{user.id}{safe_ext}"  # Always use the safe, detected extension
    file_path = os.path.join(upload_dir, filename)

    with open(file_path, "wb") as buffer:
        buffer.write(contents)

    user.profile_pic = f"uploads/{filename}"
    db.commit()
    db.refresh(user)

    return {"message": "Profile picture updated", "profile_pic": user.profile_pic}


@router.post("/logout")
def logout(response: Response):
    clear_session_cookie(response)
    response.delete_cookie("railgo_csrf", path="/")
    return {"message": "Logged out"}


# ── Change Password ────────────────────────────────────────────────────────────
class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

@router.post("/change-password")
@limiter.limit("5/minute")
def change_password(req: ChangePasswordRequest, request: Request, db: Session = Depends(get_db)):
    """Verify current password then set a new one."""
    user_id = get_current_user_id(request)
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    if not verify_password(req.current_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect.")
    if len(req.new_password) < 6:
        raise HTTPException(status_code=400, detail="New password must be at least 6 characters.")
    if req.current_password == req.new_password:
        raise HTTPException(status_code=400, detail="New password must be different from your current password.")
    user.password_hash = hash_password(req.new_password)
    db.commit()
    return {"message": "Password changed successfully."}




# ── Forgot Password ───────────────────────────────────────────────────────────
class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    email: str
    otp: str
    new_password: str

@router.post("/forgot-password")
@limiter.limit("3/minute")
def forgot_password(req: ForgotPasswordRequest, request: Request, db: Session = Depends(get_db)):
    """Generate a password-reset OTP and send it to the user's email."""
    email = req.email.lower().strip()

    # Always return 200 to prevent email enumeration attacks
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        return {"message": "If that email is registered, a reset code has been sent."}

    otp = ''.join(random.choices(string.digits, k=6))
    expires_at = datetime.utcnow() + timedelta(minutes=10)

    otp_record = db.query(models.OTPVerification).filter(models.OTPVerification.email == email).first()
    if not otp_record:
        otp_record = models.OTPVerification(email=email)
        db.add(otp_record)

    otp_record.otp = otp
    otp_record.expires_at = expires_at
    db.commit()

    send_forgot_password_email(email, otp, user.name)
    return {"message": "If that email is registered, a reset code has been sent."}


@router.post("/reset-password")
@limiter.limit("5/minute")
def reset_password(req: ResetPasswordRequest, request: Request, db: Session = Depends(get_db)):
    """Verify reset OTP and update the user's password."""
    email = req.email.lower().strip()

    if len(req.new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")

    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid request.")

    otp_record = db.query(models.OTPVerification).filter(models.OTPVerification.email == email).first()
    if not otp_record or otp_record.otp != req.otp.strip():
        raise HTTPException(status_code=400, detail="Invalid or expired reset code.")
    if otp_record.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Reset code has expired. Please request a new one.")

    user.password_hash = hash_password(req.new_password)
    db.commit()

    # Clean up the OTP record
    db.delete(otp_record)
    db.commit()

    return {"message": "Password has been reset successfully. You can now log in."}

