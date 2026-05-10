import os
import sys
from datetime import date, timedelta, time

# Add the parent directory to sys.path so we can import 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import engine, Base, SessionLocal
from app import models

def seed_data():
    # Ensure tables are created
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if data already exists
        if db.query(models.Station).first():
            print("Database already seeded. Skipping.")
            return

        print("Seeding database...")

        # 1. Add Stations
        stations_data = [
            {"code": "NDLS", "name": "New Delhi", "city": "New Delhi", "state": "Delhi"},
            {"code": "MMCT", "name": "Mumbai Central", "city": "Mumbai", "state": "Maharashtra"},
            {"code": "MAS", "name": "Chennai Central", "city": "Chennai", "state": "Tamil Nadu"},
            {"code": "HWH", "name": "Howrah Junction", "city": "Kolkata", "state": "West Bengal"}
        ]
        stations = []
        for s in stations_data:
            station = models.Station(**s)
            db.add(station)
            stations.append(station)
        db.commit()

        # 2. Add Classes
        classes_data = [
            {"code": "1A", "name": "First Class AC"},
            {"code": "2A", "name": "AC 2 Tier"},
            {"code": "3A", "name": "AC 3 Tier"},
            {"code": "SL", "name": "Sleeper"}
        ]
        class_masters = []
        for c in classes_data:
            cm = models.ClassMaster(**c)
            db.add(cm)
            class_masters.append(cm)
        db.commit()

        # 3. Add Trains
        t1 = models.Train(
            train_number="12951",
            name="Rajdhani Express",
            source_station_id=stations[1].id, # MMCT
            destination_station_id=stations[0].id, # NDLS
            departure_time=time(17, 0),
            arrival_time=time(8, 30)
        )
        t2 = models.Train(
            train_number="12621",
            name="Tamil Nadu Express",
            source_station_id=stations[2].id, # MAS
            destination_station_id=stations[0].id, # NDLS
            departure_time=time(22, 0),
            arrival_time=time(6, 30)
        )
        db.add_all([t1, t2])
        db.commit()

        # 4. Add Train Classes
        db.add(models.TrainClass(train_id=t1.id, class_id=class_masters[0].id, base_price=4500.0))
        db.add(models.TrainClass(train_id=t1.id, class_id=class_masters[1].id, base_price=3200.0))
        db.add(models.TrainClass(train_id=t1.id, class_id=class_masters[2].id, base_price=2100.0))
        
        db.add(models.TrainClass(train_id=t2.id, class_id=class_masters[1].id, base_price=2800.0))
        db.add(models.TrainClass(train_id=t2.id, class_id=class_masters[2].id, base_price=1900.0))
        db.add(models.TrainClass(train_id=t2.id, class_id=class_masters[3].id, base_price=800.0))
        db.commit()

        # 5. Add Train Instances (Next 30 days)
        today = date.today()
        for i in range(30):
            journey_date = today + timedelta(days=i)
            db.add(models.TrainInstance(train_id=t1.id, journey_date=journey_date))
            db.add(models.TrainInstance(train_id=t2.id, journey_date=journey_date))
        
        db.commit()
        print("Database seeded successfully!")

    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
