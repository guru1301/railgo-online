from app.database import SessionLocal
from app import models
from datetime import time, datetime

db = SessionLocal()

def time_or_none(t_str):
    if t_str is None or t_str in ['Start', 'End', '-']:
        return None
    return datetime.strptime(t_str, "%H:%M").time()

stops_data = [
    (1, "Chennai Egmore", "MS", None, "15:40"),
    (2, "Tambaram", "TBM", "16:05", "16:07"),
    (3, "Chengalpattu Jn", "CGL", "16:33", "16:35"),
    (4, "Melmaruvathur", "MLMR", "16:58", "17:00"),
    (5, "Villupuram Jn", "VM", "18:02", "18:05"),
    (6, "Vriddhachalam Jn", "VRI", "18:46", "18:48"),
    (7, "Pennadam", "PNDM", "19:01", "19:02"),
    (8, "Ariyalur", "ALU", "19:27", "19:28"),
    (9, "Lalgudi", "LLI", "19:59", "20:00"),
    (10, "Srirangam", "SRGM", "20:14", "20:16"),
    (11, "Ponmalai", "GOC", "20:27", "20:28"),
    (12, "Tiruchchirappalli Jn", "TPJ", "20:40", "20:45"),
    (13, "Pudukkottai", "PDKT", "21:28", "21:30"),
    (14, "Karaikkudi Jn", "KKDI", "22:30", None),
]

train = db.query(models.Train).filter(models.Train.train_number == "12605").first()

if not train:
    print("Train 12605 not found! Creating it...")
    # Get MS and KKDI
    ms = db.query(models.Station).filter(models.Station.code == "MS").first()
    kkdi = db.query(models.Station).filter(models.Station.code == "KKDI").first()
    
    train = models.Train(
        train_number="12605",
        name="Pallavan Sf Express",
        source_station_id=ms.id if ms else None,
        destination_station_id=kkdi.id if kkdi else None,
        departure_time=time(15, 40),
        arrival_time=time(22, 30)
    )
    db.add(train)
    db.commit()
    db.refresh(train)

# Delete existing stops for this train
db.query(models.TrainStop).filter(models.TrainStop.train_id == train.id).delete()
db.commit()

# Add stations and stops
distance_mock = 0
for order, name, code, arr, dep in stops_data:
    station = db.query(models.Station).filter(models.Station.code == code).first()
    if not station:
        station = models.Station(code=code, name=name, city=name, state="Tamil Nadu")
        db.add(station)
        db.commit()
        db.refresh(station)
        print(f"Created station {code}")
    
    arr_t = time_or_none(arr)
    dep_t = time_or_none(dep)
    
    stop = models.TrainStop(
        train_id=train.id,
        station_id=station.id,
        arrival_time=arr_t,
        departure_time=dep_t,
        stop_order=order,
        distance_from_source=distance_mock
    )
    db.add(stop)
    distance_mock += 30 # roughly mock distance

db.commit()
print("Successfully seeded Pallavan Express 14 stops!")
