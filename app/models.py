from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, DateTime, Time, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id            = Column(Integer, primary_key=True, index=True)
    name          = Column(String)
    email         = Column(String, unique=True, index=True)
    password_hash = Column(String)
    profile_pic   = Column(String, nullable=True)
    created_at    = Column(DateTime(timezone=True), server_default=func.now())

class OTPVerification(Base):
    __tablename__ = "otp_verifications"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    otp = Column(String)
    expires_at = Column(DateTime)


class Station(Base):
    __tablename__ = "stations"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    name = Column(String)
    city = Column(String)
    state = Column(String)

class Train(Base):
    __tablename__ = "trains"
    id = Column(Integer, primary_key=True, index=True)
    train_number = Column(String, unique=True, index=True)
    name = Column(String)
    source_station_id = Column(Integer, ForeignKey("stations.id"))
    destination_station_id = Column(Integer, ForeignKey("stations.id"))
    departure_time = Column(Time)
    arrival_time = Column(Time)

    source_station = relationship("Station", foreign_keys=[source_station_id])
    destination_station = relationship("Station", foreign_keys=[destination_station_id])
    train_classes = relationship("TrainClass", back_populates="train")
    train_instances = relationship("TrainInstance", back_populates="train")
    train_stops = relationship("TrainStop", back_populates="train", order_by="TrainStop.stop_order")

class ClassMaster(Base):
    __tablename__ = "classes"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True) # e.g. '1A', 'SL'
    name = Column(String)

class TrainClass(Base):
    __tablename__ = "train_classes"
    id = Column(Integer, primary_key=True, index=True)
    train_id = Column(Integer, ForeignKey("trains.id"))
    class_id = Column(Integer, ForeignKey("classes.id"))
    base_price = Column(Float)

    train = relationship("Train", back_populates="train_classes")
    class_master = relationship("ClassMaster")

class TrainInstance(Base):
    __tablename__ = "train_instances"
    id = Column(Integer, primary_key=True, index=True)
    train_id = Column(Integer, ForeignKey("trains.id"))
    journey_date = Column(Date)
    status = Column(String, default="Scheduled")

    train = relationship("Train", back_populates="train_instances")
    bookings = relationship("Booking", back_populates="train_instance")

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    pnr = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    train_instance_id = Column(Integer, ForeignKey("train_instances.id"))
    train_class_id = Column(Integer, ForeignKey("train_classes.id"))
    booking_date = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, default="Confirmed")
    payment_status = Column(String, default="PENDING")  # PENDING / PAID / FAILED
    razorpay_order_id = Column(String, nullable=True)
    razorpay_payment_id = Column(String, nullable=True)
    total_amount = Column(Float)
    contact_email = Column(String)
    contact_phone = Column(String)

    train_instance = relationship("TrainInstance", back_populates="bookings")
    train_class = relationship("TrainClass")
    passengers = relationship("Passenger", back_populates="booking", cascade="all, delete-orphan")

class Passenger(Base):
    __tablename__ = "passengers"
    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"))
    name = Column(String)
    age = Column(Integer)
    gender = Column(String)
    seat_number = Column(String, nullable=True)

    booking = relationship("Booking", back_populates="passengers")

class TrainStop(Base):
    __tablename__ = "train_stops"
    id = Column(Integer, primary_key=True, index=True)
    train_id = Column(Integer, ForeignKey("trains.id"))
    station_id = Column(Integer, ForeignKey("stations.id"))
    arrival_time = Column(Time)
    departure_time = Column(Time)
    stop_order = Column(Integer)
    distance_from_source = Column(Float)

    train = relationship("Train", back_populates="train_stops")
    station = relationship("Station")
