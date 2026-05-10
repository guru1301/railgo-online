"""
Seed: Vaigai SF Exp (12635) + Chozhan SF Exp (22675)
Run: python scratch/seed_vaigai_chozhan.py
"""
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date, time
from app.database import SessionLocal
from app import models

db = SessionLocal()

def t(s):
    if s is None: return None
    h, m = map(int, s.split(":"))
    return time(h, m)

def ensure_stations(stations):
    for s in stations:
        if not db.query(models.Station).filter(models.Station.code == s["code"]).first():
            db.add(models.Station(**s))
            print(f"  + Station: {s['code']} - {s['name']}")
        else:
            print(f"  = Exists:  {s['code']}")
    db.commit()

def add_train(train_number, name, train_type, classes, stops, dates):
    print(f"\n>>> Adding {train_number} - {name}")

    train = db.query(models.Train).filter(models.Train.train_number == train_number).first()
    if train:
        db.query(models.TrainStop).filter(models.TrainStop.train_id == train.id).delete()
        db.commit()
        print(f"  = Train exists, refreshing stops...")
    else:
        train = models.Train(train_number=train_number, name=name)
        db.add(train)
        db.flush()
        print(f"  + Train created id={train.id}")

    # Classes
    for cls_code, price in classes:
        cls_master = db.query(models.ClassMaster).filter(models.ClassMaster.code == cls_code).first()
        if not cls_master:
            print(f"  ! ClassMaster '{cls_code}' not found, skipping")
            continue
        exists = db.query(models.TrainClass).filter(
            models.TrainClass.train_id == train.id,
            models.TrainClass.class_id == cls_master.id
        ).first()
        if not exists:
            db.add(models.TrainClass(train_id=train.id, class_id=cls_master.id, base_price=price))
            print(f"  + Class: {cls_code} @ Rs.{price}")

    # Stops
    for order, (code, arr, dep, dist) in enumerate(stops, start=1):
        station = db.query(models.Station).filter(models.Station.code == code).first()
        if not station:
            print(f"  ! Station {code} not found!")
            continue
        db.add(models.TrainStop(
            train_id=train.id, station_id=station.id,
            stop_order=order, arrival_time=t(arr),
            departure_time=t(dep), distance_from_source=dist
        ))
        print(f"  + Stop {order}: {code} arr={arr} dep={dep}")

    # Instances
    for jdate in dates:
        exists = db.query(models.TrainInstance).filter(
            models.TrainInstance.train_id == train.id,
            models.TrainInstance.journey_date == jdate
        ).first()
        if not exists:
            db.add(models.TrainInstance(train_id=train.id, journey_date=jdate))
    print(f"  + {len(dates)} journey dates added")
    db.commit()

# ── STEP 1: New Stations ─────────────────────────────────────────────────────
print("=== Ensuring all stations exist ===")
ensure_stations([
    {"code": "MPA",  "name": "Manaparai",          "city": "Manaparai",       "state": "Tamil Nadu"},
    {"code": "DG",   "name": "Dindigul Jn",         "city": "Dindigul",        "state": "Tamil Nadu"},
    {"code": "SDN",  "name": "Sholavandan",          "city": "Sholavandan",     "state": "Tamil Nadu"},
    {"code": "KON",  "name": "Kudalnagar",           "city": "Madurai",         "state": "Tamil Nadu"},
    {"code": "MDU",  "name": "Madurai Jn",           "city": "Madurai",         "state": "Tamil Nadu"},
    {"code": "MBM",  "name": "Mambalam",             "city": "Chennai",         "state": "Tamil Nadu"},
    {"code": "TMV",  "name": "Tindivanam",           "city": "Tindivanam",      "state": "Tamil Nadu"},
    {"code": "PRT",  "name": "Panruti",              "city": "Panruti",         "state": "Tamil Nadu"},
    {"code": "TDPR", "name": "Tirupadripulyur",      "city": "Cuddalore",       "state": "Tamil Nadu"},
    {"code": "CUPJ", "name": "Cuddalore Port Jn",    "city": "Cuddalore",       "state": "Tamil Nadu"},
    {"code": "CDM",  "name": "Chidambaram",          "city": "Chidambaram",     "state": "Tamil Nadu"},
    {"code": "SY",   "name": "Sirkazhi",             "city": "Sirkazhi",        "state": "Tamil Nadu"},
    {"code": "VDL",  "name": "Vaitisvarankoil",      "city": "Vaitisvarankoil", "state": "Tamil Nadu"},
    {"code": "MV",   "name": "Mayiladuturai Jn",     "city": "Mayiladuturai",   "state": "Tamil Nadu"},
    {"code": "ADT",  "name": "Aduturai",             "city": "Aduturai",        "state": "Tamil Nadu"},
    {"code": "KMU",  "name": "Kumbakonam",           "city": "Kumbakonam",      "state": "Tamil Nadu"},
    {"code": "PML",  "name": "Papanasam",            "city": "Papanasam",       "state": "Tamil Nadu"},
    {"code": "TJ",   "name": "Thanjavur Jn",         "city": "Thanjavur",       "state": "Tamil Nadu"},
    {"code": "BAL",  "name": "Budalur",              "city": "Budalur",         "state": "Tamil Nadu"},
    {"code": "TRB",  "name": "Tiruverumbur",         "city": "Tiruchirappalli", "state": "Tamil Nadu"},
])

# Journey dates — today + next 20 days
from datetime import datetime, timedelta
today = datetime.now().date()
dates = [today + timedelta(days=i) for i in range(21)]

# ── TRAIN 1: 12635 Vaigai SF Express ─────────────────────────────────────────
add_train(
    train_number="12635",
    name="Vaigai Sf Express",
    train_type=None,
    classes=[
        ("2S", 180),
        ("CC", 650),
    ],
    stops=[
        # (code, arrival, departure, distance_km)
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
    dates=dates
)

# ── TRAIN 2: 22675 Chozhan SF Express ────────────────────────────────────────
add_train(
    train_number="22675",
    name="Chozhan Sf Express",
    train_type=None,
    classes=[
        ("2S",  180),
        ("SL",  350),
        ("3A",  900),
        ("2A",  1200),
        ("1A",  2000),
    ],
    stops=[
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
    dates=dates
)

db.close()
print("\n=== All done! Both trains seeded successfully ===")
