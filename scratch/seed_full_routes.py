import os
import sys
from datetime import date, timedelta, time, datetime

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app import models

db = SessionLocal()

def t(s):
    if s is None or s == "": return None
    h, m = map(int, s.split(":"))
    return time(h, m)

def ensure_classes():
    print("Ensuring all classes exist...")
    classes_data = [
        {"code": "1A", "name": "First Class AC"},
        {"code": "2A", "name": "AC 2 Tier"},
        {"code": "3A", "name": "AC 3 Tier"},
        {"code": "SL", "name": "Sleeper"},
        {"code": "2S", "name": "Second Sitting"},
        {"code": "CC", "name": "AC Chair Car"}
    ]
    for c in classes_data:
        if not db.query(models.ClassMaster).filter(models.ClassMaster.code == c["code"]).first():
            db.add(models.ClassMaster(**c))
            print(f"  + Added Class: {c['code']}")
    db.commit()

def add_train_with_stops(train_number, name, classes, stops, dates):
    print(f"\n>>> Processing Train {train_number} - {name}")

    # 1. Ensure Source and Destination Stations Exist
    source_code = stops[0][0]
    dest_code = stops[-1][0]
    
    def get_or_create_station(code):
        st = db.query(models.Station).filter(models.Station.code == code).first()
        if not st:
            st = models.Station(code=code, name=code, city=code, state="Tamil Nadu")
            db.add(st)
            db.flush()
            print(f"  + Created Station: {code}")
        return st

    source_st = get_or_create_station(source_code)
    dest_st = get_or_create_station(dest_code)

    # 2. Create or Get Train
    train = db.query(models.Train).filter(models.Train.train_number == train_number).first()
    
    if train:
        print(f"  = Train exists, updating details...")
        train.name = name
        train.source_station_id = source_st.id
        train.destination_station_id = dest_st.id
        train.departure_time = t(stops[0][2])
        train.arrival_time = t(stops[-1][1])
    else:
        train = models.Train(
            train_number=train_number, 
            name=name,
            source_station_id=source_st.id,
            destination_station_id=dest_st.id,
            departure_time=t(stops[0][2]),
            arrival_time=t(stops[-1][1])
        )
        db.add(train)
        db.flush()
        print(f"  + Created Train id={train.id}")

    # 2. Add Classes
    for cls_code, price in classes:
        cls_master = db.query(models.ClassMaster).filter(models.ClassMaster.code == cls_code).first()
        if not cls_master:
            print(f"  ! Class {cls_code} not found in Master!")
            continue
        exists = db.query(models.TrainClass).filter(
            models.TrainClass.train_id == train.id,
            models.TrainClass.class_id == cls_master.id
        ).first()
        if not exists:
            db.add(models.TrainClass(train_id=train.id, class_id=cls_master.id, base_price=price))
            print(f"  + Class: {cls_code} @ {price}")

    # 3. Add Stops (Refresh them)
    db.query(models.TrainStop).filter(models.TrainStop.train_id == train.id).delete()
    for order, (code, arr, dep, dist) in enumerate(stops, start=1):
        station = db.query(models.Station).filter(models.Station.code == code).first()
        if not station:
            # Create missing station with dummy state
            station = models.Station(code=code, name=code, city=code, state="Tamil Nadu")
            db.add(station)
            db.flush()
            print(f"  + Created missing station: {code}")
            
        db.add(models.TrainStop(
            train_id=train.id, station_id=station.id,
            stop_order=order, arrival_time=t(arr),
            departure_time=t(dep), distance_from_source=dist
        ))
    print(f"  + {len(stops)} stops added")

    # 4. Add Instances
    for jdate in dates:
        exists = db.query(models.TrainInstance).filter(
            models.TrainInstance.train_id == train.id,
            models.TrainInstance.journey_date == jdate
        ).first()
        if not exists:
            db.add(models.TrainInstance(train_id=train.id, journey_date=jdate))
    print(f"  + {len(dates)} journey dates ensured")
    db.commit()

def seed_full_routes():
    ensure_classes()
    
    today = date.today()
    dates = [today + timedelta(days=i) for i in range(30)]

    # 1. PALLAVAN EXPRESS (12605)
    add_train_with_stops(
        "12605", "Pallavan Sf Express",
        [("2S", 160), ("CC", 580)],
        [
            ("MS",   None,    "15:40",  0),
            ("TBM",  "16:05", "16:07",  30),
            ("CGL",  "16:33", "16:35",  56),
            ("MLMR", "16:58", "17:00",  75),
            ("VM",   "18:02", "18:05",  160),
            ("VRI",  "18:46", "18:48",  214),
            ("PNDM", "19:01", "19:02",  230),
            ("ALU",  "19:27", "19:28",  261),
            ("LLI",  "19:59", "20:00",  310),
            ("SRGM", "20:14", "20:16",  320),
            ("GOC",  "20:27", "20:28",  330),
            ("TPJ",  "20:40", "20:45",  332),
            ("PDKT", "21:28", "21:30",  380),
            ("KKDI", "22:30", None,     420),
        ],
        dates
    )

    # 2. VAIGAI EXPRESS (12635)
    add_train_with_stops(
        "12635", "Vaigai Sf Express",
        [("2S", 180), ("CC", 650)],
        [
            ("MS",   None,    "13:15",  0),
            ("TBM",  "13:40", "13:42",  30),
            ("CGL",  "14:08", "14:10",  56),
            ("MLMR", "14:29", "14:30",  75),
            ("VM",   "15:30", "15:35",  160),
            ("VRI",  "16:14", "16:16",  214),
            ("ALU",  "16:49", "16:50",  261),
            ("SRGM", "17:30", "17:32",  312),
            ("TPJ",  "18:05", "18:10",  332),
            ("MPA",  "18:39", "18:40",  373),
            ("DG",   "19:17", "19:20",  421),
            ("SDN",  "19:49", "19:50",  452),
            ("KON",  "19:52", "19:53",  454),
            ("MDU",  "20:35", None,     469),
        ],
        dates
    )

    # 3. CHOZHAN EXPRESS (22675)
    add_train_with_stops(
        "22675", "Chozhan Sf Express",
        [("2S", 180), ("SL", 350), ("3A", 900), ("2A", 1200), ("1A", 2000)],
        [
            ("MS",   None,    "08:00",  0),
            ("MBM",  "08:13", "08:15",  8),
            ("TBM",  "08:25", "08:27",  30),
            ("CGL",  "08:53", "08:55",  56),
            ("MLMR", "09:18", "09:20",  75),
            ("TMV",  "09:43", "09:45",  105),
            ("VM",   "10:40", "10:45",  160),
            ("PRT",  "11:07", "11:08",  189),
            ("TDPR", "11:27", "11:28",  207),
            ("CUPJ", "11:34", "11:35",  213),
            ("CDM",  "12:03", "12:05",  241),
            ("SY",   "12:20", "12:21",  258),
            ("VDL",  "12:27", "12:28",  264),
            ("MV",   "12:48", "12:50",  280),
            ("ADT",  "13:10", "13:11",  299),
            ("KMU",  "13:22", "13:24",  310),
            ("PML",  "13:33", "13:34",  320),
            ("TJ",   "13:54", "13:56",  340),
            ("BAL",  "14:11", "14:12",  356),
            ("TRB",  "14:27", "14:28",  370),
            ("GOC",  "14:49", "14:50",  382),
            ("TPJ",  "15:15", None,     390),
        ],
        dates
    )

    print("\n--- Seeding Complete! ---")

if __name__ == "__main__":
    seed_full_routes()
    db.close()
