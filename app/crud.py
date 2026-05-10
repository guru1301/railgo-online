from sqlalchemy.orm import Session, aliased
from app import models, schemas
from datetime import date

def get_stations(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Station).offset(skip).limit(limit).all()

def search_trains(db: Session, source_code: str, destination_code: str, journey_date: date):
    # Find stations
    source = db.query(models.Station).filter(models.Station.code == source_code).first()
    destination = db.query(models.Station).filter(models.Station.code == destination_code).first()
    
    if not source or not destination:
        return []

    SourceStop = aliased(models.TrainStop)
    DestStop = aliased(models.TrainStop)

    # Find train instances
    results = db.query(models.TrainInstance, SourceStop, DestStop)\
        .join(models.Train, models.TrainInstance.train_id == models.Train.id)\
        .join(SourceStop, models.Train.id == SourceStop.train_id)\
        .join(DestStop, models.Train.id == DestStop.train_id)\
        .filter(
            SourceStop.station_id == source.id,
            DestStop.station_id == destination.id,
            SourceStop.stop_order < DestStop.stop_order,
            models.TrainInstance.journey_date == journey_date
        ).all()
    
    return results

def create_booking(db: Session, booking: schemas.BookingCreate, pnr: str, total_amount: float,
                   payment_status: str = "PENDING", razorpay_order_id: str = None,
                   razorpay_payment_id: str = None):
    db_booking = models.Booking(
        pnr=pnr,
        user_id=booking.user_id,
        train_instance_id=booking.train_instance_id,
        train_class_id=booking.train_class_id,
        total_amount=total_amount,
        contact_email=booking.contact_email,
        contact_phone=booking.contact_phone,
        status="Confirmed",
        payment_status=payment_status,
        razorpay_order_id=razorpay_order_id,
        razorpay_payment_id=razorpay_payment_id
    )
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    
    for passenger_data in booking.passengers:
        db_passenger = models.Passenger(
            booking_id=db_booking.id,
            name=passenger_data.name,
            age=passenger_data.age,
            gender=passenger_data.gender
        )
        db.add(db_passenger)
    
    db.commit()
    db.refresh(db_booking)
    return db_booking

def get_booking_by_pnr(db: Session, pnr: str):
    return db.query(models.Booking).filter(models.Booking.pnr == pnr).first()

def get_booking(db: Session, booking_id: int):
    return db.query(models.Booking).filter(models.Booking.id == booking_id).first()

def get_train_schedule(db: Session, train_number: str):
    train = db.query(models.Train).filter(models.Train.train_number == train_number).first()
    if not train:
        return None
    
    stops = db.query(models.TrainStop).filter(models.TrainStop.train_id == train.id).order_by(models.TrainStop.stop_order).all()
    return stops
