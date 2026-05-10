from fastapi import APIRouter, Depends, HTTPException, Header, Request
from sqlalchemy.orm import Session, joinedload
import time
import random
import hmac
import hashlib
import requests as http_requests
import base64
from app import crud, schemas, database, models
from app.auth import decode_token
from app.security import get_current_user_id, get_token_from_request
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/api/bookings", tags=["bookings"])

# ── Razorpay credentials ──────────────────────────────────────────────────────
RAZORPAY_KEY_ID     = "rzp_test_SlMpbTRhyixc23"
RAZORPAY_KEY_SECRET = "PvFv90ykV5KoxV2Dhdzeoogn"

def _rzp_auth():
    token = base64.b64encode(f"{RAZORPAY_KEY_ID}:{RAZORPAY_KEY_SECRET}".encode()).decode()
    return {"Authorization": f"Basic {token}", "Content-Type": "application/json"}

def generate_pnr():
    return "RG" + str(int(time.time())) + str(random.randint(100, 999))

# ── Pydantic request models ───────────────────────────────────────────────────
class FrontendPassenger(BaseModel):
    name: str
    age: int
    gender: str

class FrontendContactDetails(BaseModel):
    email: str
    phone: str

class CreateOrderRequest(BaseModel):
    trainNumber: str
    date: str
    classType: str
    passengerCount: int

class VerifyPaymentRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    trainNumber: str
    date: str
    classType: str
    passengers: List[FrontendPassenger]
    contactDetails: FrontendContactDetails

# ── Helper: fetch booking with all relations ──────────────────────────────────
def _load_booking(db: Session, booking_id: int):
    return db.query(models.Booking).options(
        joinedload(models.Booking.train_instance).joinedload(models.TrainInstance.train)
            .joinedload(models.Train.source_station),
        joinedload(models.Booking.train_instance).joinedload(models.TrainInstance.train)
            .joinedload(models.Train.destination_station),
        joinedload(models.Booking.train_class).joinedload(models.TrainClass.class_master),
        joinedload(models.Booking.passengers),
    ).filter(models.Booking.id == booking_id).first()

# ── POST /api/bookings/create-order ──────────────────────────────────────────
@router.post("/create-order")
def create_order(
    req: CreateOrderRequest,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(database.get_db)
):
    """Create a Razorpay order server-side and return the order_id + amount."""
    train = db.query(models.Train).filter(models.Train.train_number == req.trainNumber).first()
    if not train:
        raise HTTPException(status_code=404, detail="Train not found")

    # Find the requested class and its price
    train_class = None
    for tc in train.train_classes:
        if tc.class_master.code == req.classType:
            train_class = tc
            break
    if not train_class:
        raise HTTPException(status_code=404, detail="Train class not found")

    base_fare    = train_class.base_price * req.passengerCount
    conv_fee     = 30
    gst          = round((base_fare + conv_fee) * 0.05)
    total_amount = base_fare + conv_fee + gst

    # Create Razorpay order
    receipt = f"rcpt_{int(time.time())}_{random.randint(100,999)}"
    try:
        rz_resp = http_requests.post(
            "https://api.razorpay.com/v1/orders",
            headers=_rzp_auth(),
            json={"amount": int(total_amount * 100), "currency": "INR", "receipt": receipt},
            timeout=10
        )
        rz_data = rz_resp.json()
        if rz_resp.status_code != 200:
            raise HTTPException(status_code=502, detail=rz_data.get("error", {}).get("description", "Razorpay error"))
    except http_requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Could not reach Razorpay: {str(e)}")

    return {
        "order_id":   rz_data["id"],
        "amount":     total_amount,
        "amount_paise": int(total_amount * 100),
        "currency":   "INR",
        "key_id":     RAZORPAY_KEY_ID,
        "base_fare":  base_fare,
        "conv_fee":   conv_fee,
        "gst":        gst,
    }

# ── POST /api/bookings/verify-payment ────────────────────────────────────────
@router.post("/verify-payment")
def verify_payment(
    req: VerifyPaymentRequest,
    request: Request,
    db: Session = Depends(database.get_db)
):
    """Verify Razorpay HMAC signature, save booking, return bookingId + PNR."""
    # 1. Verify signature
    msg = f"{req.razorpay_order_id}|{req.razorpay_payment_id}"
    expected_sig = hmac.new(
        RAZORPAY_KEY_SECRET.encode("utf-8"),
        msg.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(expected_sig, req.razorpay_signature):
        raise HTTPException(status_code=400, detail="Payment verification failed: invalid signature")

    # 2. Resolve user
    user_id = None
    token = get_token_from_request(request)
    if token:
        payload = decode_token(token)
        if payload and "sub" in payload:
            user_id = int(payload["sub"])

    # 3. Resolve train + class + instance
    train = db.query(models.Train).filter(models.Train.train_number == req.trainNumber).first()
    if not train:
        raise HTTPException(status_code=404, detail="Train not found")

    journey_date = datetime.strptime(req.date, "%Y-%m-%d").date()
    train_instance = db.query(models.TrainInstance).filter(
        models.TrainInstance.train_id == train.id,
        models.TrainInstance.journey_date == journey_date
    ).first()
    if not train_instance:
        raise HTTPException(status_code=404, detail="Train instance not found")

    train_class = None
    for tc in train.train_classes:
        if tc.class_master.code == req.classType:
            train_class = tc
            break
    if not train_class:
        raise HTTPException(status_code=404, detail="Train class not found")

    # 4. Calculate total (same formula as create-order)
    n = len(req.passengers)
    base_fare    = train_class.base_price * n
    conv_fee     = 30
    gst          = round((base_fare + conv_fee) * 0.05)
    total_amount = base_fare + conv_fee + gst

    # 5. Save booking
    booking_create = schemas.BookingCreate(
        user_id=user_id,
        train_instance_id=train_instance.id,
        train_class_id=train_class.id,
        passengers=[schemas.PassengerCreate(name=p.name, age=p.age, gender=p.gender) for p in req.passengers],
        contact_email=req.contactDetails.email,
        contact_phone=req.contactDetails.phone
    )

    pnr = generate_pnr()
    db_booking = crud.create_booking(
        db=db,
        booking=booking_create,
        pnr=pnr,
        total_amount=total_amount,
        payment_status="PAID",
        razorpay_order_id=req.razorpay_order_id,
        razorpay_payment_id=req.razorpay_payment_id
    )

    return {"success": True, "bookingId": db_booking.id, "pnr": pnr}

# ── GET /api/bookings/user/my-bookings ───────────────────────────────────────
@router.get("/user/my-bookings", response_model=List[schemas.Booking])
def get_my_bookings(
    request: Request,
    db: Session = Depends(database.get_db)
):
    user_id = get_current_user_id(request)
    bookings = db.query(models.Booking).options(
        joinedload(models.Booking.train_instance).joinedload(models.TrainInstance.train)
            .joinedload(models.Train.source_station),
        joinedload(models.Booking.train_instance).joinedload(models.TrainInstance.train)
            .joinedload(models.Train.destination_station),
        joinedload(models.Booking.train_class).joinedload(models.TrainClass.class_master),
        joinedload(models.Booking.passengers),
    ).filter(models.Booking.user_id == user_id).order_by(models.Booking.id.desc()).all()

    return bookings

# ── GET /api/bookings/{booking_id} ───────────────────────────────────────────
@router.get("/{booking_id}", response_model=schemas.Booking)
def get_booking(booking_id: int, db: Session = Depends(database.get_db)):
    db_booking = _load_booking(db, booking_id)
    if not db_booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return db_booking
