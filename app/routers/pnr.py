from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, schemas, database, models
from app.email_utils import send_otp_email, send_cancel_otp_email
import random
import string
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/pnr-status", tags=["pnr"])

@router.get("/check/{pnr}", response_model=schemas.Booking)
def check_pnr(pnr: str, db: Session = Depends(database.get_db)):
    db_booking = crud.get_booking_by_pnr(db, pnr=pnr)
    if not db_booking:
        raise HTTPException(status_code=404, detail="PNR not found")
    return db_booking

@router.post("/{pnr}/cancel-otp")
def send_cancel_otp(pnr: str, db: Session = Depends(database.get_db)):
    db_booking = crud.get_booking_by_pnr(db, pnr=pnr)
    if not db_booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if db_booking.status.upper() == "CANCELLED":
        raise HTTPException(status_code=400, detail="Booking is already cancelled")
    
    email = db_booking.contact_email
    if not email:
        raise HTTPException(status_code=400, detail="No contact email found for this booking")

    otp = ''.join(random.choices(string.digits, k=6))
    expires_at = datetime.utcnow() + timedelta(minutes=10)
    
    otp_record = db.query(models.OTPVerification).filter(models.OTPVerification.email == email).first()
    if not otp_record:
        otp_record = models.OTPVerification(email=email)
        db.add(otp_record)
        
    otp_record.otp = otp
    otp_record.expires_at = expires_at
    db.commit()
    
    success = send_cancel_otp_email(email, otp, pnr)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to send OTP email")
        
    return {"message": f"OTP sent to {email}"}

@router.post("/{pnr}/cancel-confirm")
def confirm_cancel(pnr: str, req: schemas.CancelConfirmRequest, db: Session = Depends(database.get_db)):
    db_booking = crud.get_booking_by_pnr(db, pnr=pnr)
    if not db_booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if db_booking.status.upper() == "CANCELLED":
        raise HTTPException(status_code=400, detail="Booking is already cancelled")
        
    email = db_booking.contact_email
    otp_record = db.query(models.OTPVerification).filter(models.OTPVerification.email == email).first()
    if not otp_record or otp_record.otp != req.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    if otp_record.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="OTP has expired")
        
    # Mark the booking as cancelled instead of deleting it
    db_booking.status = "CANCELLED"
    db.commit()
    
    # Also delete the OTP record
    db.delete(otp_record)
    db.commit()
    
    return {"success": True, "message": "Booking successfully cancelled"}
