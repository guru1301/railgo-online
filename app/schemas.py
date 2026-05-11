from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime, time

class StationBase(BaseModel):
    code: str
    name: str
    city: str
    state: str

class Station(StationBase):
    id: int
    class Config:
        from_attributes = True

class ClassMaster(BaseModel):
    id: int
    code: str
    name: str
    class Config:
        from_attributes = True

class TrainClass(BaseModel):
    id: int
    class_master: ClassMaster
    base_price: float
    class Config:
        from_attributes = True

class TrainBase(BaseModel):
    train_number: str
    name: str
    departure_time: time
    arrival_time: time

class Train(TrainBase):
    id: int
    source_station: Station
    destination_station: Station
    train_classes: List[TrainClass] = []
    class Config:
        from_attributes = True

class TrainInstanceBase(BaseModel):
    journey_date: date
    status: str

class TrainInstance(TrainInstanceBase):
    id: int
    train: Train
    class Config:
        from_attributes = True

class PassengerBase(BaseModel):
    name: str
    age: int
    gender: str

class PassengerCreate(PassengerBase):
    pass

class Passenger(PassengerBase):
    id: int
    seat_number: Optional[str] = None
    class Config:
        from_attributes = True

class BookingCreate(BaseModel):
    user_id: Optional[int] = None
    train_instance_id: int
    train_class_id: int
    passengers: List[PassengerCreate]
    contact_email: str
    contact_phone: str

class Booking(BaseModel):
    id: int
    user_id: Optional[int] = None
    pnr: str
    train_instance: TrainInstance
    train_class: TrainClass
    booking_date: datetime
    status: str
    payment_status: str
    razorpay_order_id: Optional[str] = None
    razorpay_payment_id: Optional[str] = None
    total_amount: float
    contact_email: str
    contact_phone: str
    passengers: List[Passenger]

    class Config:
        from_attributes = True

class TrainSearchRequest(BaseModel):
    source: str
    destination: str
    date: date
    classType: Optional[str] = None

class CancelConfirmRequest(BaseModel):
    otp: str

class SavedPassengerCreate(BaseModel):
    name: str
    age: int
    gender: str

class SavedPassengerUpdate(BaseModel):
    name: str
    age: int
    gender: str

class SavedPassenger(BaseModel):
    id: int
    name: str
    age: int
    gender: str
    class Config:
        from_attributes = True

