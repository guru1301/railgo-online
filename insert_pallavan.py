import os
import sys
from datetime import date, timedelta, time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import engine, Base, SessionLocal
from app import models

def insert_pallavan():
    db = SessionLocal()
    try:
        print("Inserting Pallavan Express data...")

        # 1. Add Stations
        stations_data = [
            {"code": "MS", "name": "Chennai Egmore", "city": "Chennai", "state": "Tamil Nadu"},
            {"code": "TBM", "name": "Tambaram", "city": "Chennai", "state": "Tamil Nadu"},
            {"code": "CGL", "name": "Chengalpattu", "city": "Chengalpattu", "state": "Tamil Nadu"},
            {"code": "MLMR", "name": "Melmaruvattur", "city": "Melmaruvattur", "state": "Tamil Nadu"},
            {"code": "VM", "name": "Villupuram Jn", "city": "Villupuram", "state": "Tamil Nadu"},
            {"code": "VRI", "name": "Vridhachalam Jn", "city": "Vridhachalam", "state": "Tamil Nadu"},
            {"code": "PNDM", "name": "Pennadam", "city": "Pennadam", "state": "Tamil Nadu"},
            {"code": "ALU", "name": "Ariyalur", "city": "Ariyalur", "state": "Tamil Nadu"},
            {"code": "LLI", "name": "Lalgudi", "city": "Lalgudi", "state": "Tamil Nadu"},
            {"code": "SRGM", "name": "Srirangam", "city": "Tiruchirappalli", "state": "Tamil Nadu"},
            {"code": "GOC", "name": "Ponmalai Golden Rock", "city": "Tiruchirappalli", "state": "Tamil Nadu"},
            {"code": "TPJ", "name": "Tiruchirappalli", "city": "Tiruchirappalli", "state": "Tamil Nadu"},
            {"code": "PDKT", "name": "Pudukkottai", "city": "Pudukkottai", "state": "Tamil Nadu"},
            {"code": "KKDI", "name": "Karaikkudi Jn", "city": "Karaikkudi", "state": "Tamil Nadu"}
        ]
        
        for s_data in stations_data:
            existing = db.query(models.Station).filter(models.Station.code == s_data["code"]).first()
            if not existing:
                db.add(models.Station(**s_data))
        
        db.commit()

        # 2. Add Missing Classes (CC, 2S)
        missing_classes = [
            {"code": "CC", "name": "Chair Car"},
            {"code": "2S", "name": "Second Seating"}
        ]
        for c_data in missing_classes:
            existing = db.query(models.ClassMaster).filter(models.ClassMaster.code == c_data["code"]).first()
            if not existing:
                db.add(models.ClassMaster(**c_data))
        db.commit()

        # Get stations for train
        ms_station = db.query(models.Station).filter(models.Station.code == "MS").first()
        kkdi_station = db.query(models.Station).filter(models.Station.code == "KKDI").first()
        
        # 3. Add Train
        existing_train = db.query(models.Train).filter(models.Train.train_number == "12605").first()
        if not existing_train:
            t1 = models.Train(
                train_number="12605",
                name="Pallavan Sf Express",
                source_station_id=ms_station.id,
                destination_station_id=kkdi_station.id,
                departure_time=time(15, 40),
                arrival_time=time(22, 30)
            )
            db.add(t1)
            db.commit()
            db.refresh(t1)
            
            # Get class masters
            cc_class = db.query(models.ClassMaster).filter(models.ClassMaster.code == "CC").first()
            ss_class = db.query(models.ClassMaster).filter(models.ClassMaster.code == "2S").first()
            
            # 4. Add Train Classes
            db.add(models.TrainClass(train_id=t1.id, class_id=cc_class.id, base_price=650.0))
            db.add(models.TrainClass(train_id=t1.id, class_id=ss_class.id, base_price=180.0))
            db.commit()
            
            # 5. Add Train Instances (Next 30 days)
            today = date.today()
            for i in range(30):
                journey_date = today + timedelta(days=i)
                db.add(models.TrainInstance(train_id=t1.id, journey_date=journey_date))
            
            db.commit()
            print("Pallavan Express inserted successfully!")
        else:
            print("Pallavan Express already exists.")

    finally:
        db.close()

if __name__ == "__main__":
    insert_pallavan()
