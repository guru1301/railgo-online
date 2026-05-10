import os
import sys
from datetime import time

# Add the parent directory to sys.path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine, Base
from app.models import Train, Station, TrainStop

def get_or_create_station(db, code, name, city="", state=""):
    station = db.query(Station).filter(Station.code == code).first()
    if not station:
        station = Station(code=code, name=name, city=city, state=state)
        db.add(station)
        db.commit()
        db.refresh(station)
    return station

def parse_time(time_str):
    if not time_str or time_str == "Starts" or time_str == "End":
        return None
    h, m = map(int, time_str.split(':'))
    return time(h, m)

def main():
    # Ensure tables are created
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # 1. Rajdhani Express (12431)
    rajdhani = db.query(Train).filter(Train.train_number == "12431").first()
    if rajdhani:
        db.query(TrainStop).filter(TrainStop.train_id == rajdhani.id).delete()
        s1 = TrainStop(
            train_id=rajdhani.id,
            station_id=rajdhani.source_station_id,
            arrival_time=rajdhani.departure_time,
            departure_time=rajdhani.departure_time,
            stop_order=1,
            distance_from_source=0
        )
        s2 = TrainStop(
            train_id=rajdhani.id,
            station_id=rajdhani.destination_station_id,
            arrival_time=rajdhani.arrival_time,
            departure_time=rajdhani.arrival_time,
            stop_order=2,
            distance_from_source=1500 # rough estimate
        )
        db.add_all([s1, s2])

    # 2. Tamil Nadu Express (12621)
    tn_express = db.query(Train).filter(Train.train_number == "12621").first()
    if tn_express:
        db.query(TrainStop).filter(TrainStop.train_id == tn_express.id).delete()
        s1 = TrainStop(
            train_id=tn_express.id,
            station_id=tn_express.source_station_id,
            arrival_time=tn_express.departure_time,
            departure_time=tn_express.departure_time,
            stop_order=1,
            distance_from_source=0
        )
        s2 = TrainStop(
            train_id=tn_express.id,
            station_id=tn_express.destination_station_id,
            arrival_time=tn_express.arrival_time,
            departure_time=tn_express.arrival_time,
            stop_order=2,
            distance_from_source=2100 # rough estimate
        )
        db.add_all([s1, s2])

    # 3. Pallavan Express (12605)
    pallavan = db.query(Train).filter(Train.train_number == "12605").first()
    if pallavan:
        db.query(TrainStop).filter(TrainStop.train_id == pallavan.id).delete()
        
        stops_data = [
            ("MS", "Chennai Egmore", "15:40", "15:40", 0),
            ("TBM", "Tambaram", "16:05", "16:07", 24),
            ("CGL", "Chengalpattu", "16:33", "16:35", 56),
            ("MLMR", "Melmaruvattur", "16:58", "17:00", 92),
            ("VM", "Villupuram Jn", "18:02", "18:05", 159),
            ("VRI", "Vridhachalam Jn", "18:46", "18:48", 213),
            ("PNDM", "Pennadam", "19:01", "19:02", 231),
            ("ALU", "Ariyalur", "19:27", "19:28", 267),
            ("LLI", "Lalgudi", "19:59", "20:00", 310),
            ("SRGM", "Srirangam", "20:14", "20:16", 325),
            ("GOC", "Ponmalai Golden Rock", "20:27", "20:28", 334),
            ("TPJ", "Tiruchirappalli", "20:40", "20:45", 336),
            ("PDKT", "Pudukkottai", "21:28", "21:30", 389),
            ("KKDI", "Karaikkudi Jn", "23:59", "23:59", 426) # Using 23:59 instead of 00:00 to keep it on the same day for simplicity
        ]
        
        for i, (code, name, arr, dep, dist) in enumerate(stops_data):
            station = get_or_create_station(db, code, name)
            stop = TrainStop(
                train_id=pallavan.id,
                station_id=station.id,
                arrival_time=parse_time(arr),
                departure_time=parse_time(dep),
                stop_order=i + 1,
                distance_from_source=dist
            )
            db.add(stop)

    db.commit()
    db.close()
    print("Routes updated successfully.")

if __name__ == "__main__":
    main()
