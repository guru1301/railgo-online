"""
RailGo - Add New Train Route Script
=====================================
HOW TO USE:
1. Copy this file and rename it (e.g. add_12606.py)
2. Fill in the TRAIN_INFO and STOPS sections below
3. Fill in the journey DATES the train runs on
4. Run: python add_train.py

STATION CODES: Use existing codes already in DB, or add new ones under STATIONS.
TIMES: Use "HH:MM" format or None for origin/terminus (no arr/dep respectively).
"""

import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import date, time
from app.database import SessionLocal
from app import models

db = SessionLocal()

# ─────────────────────────────────────────────────────────────────────────────
#  STEP 1: Add any NEW stations (skip if they already exist in DB)
# ─────────────────────────────────────────────────────────────────────────────
NEW_STATIONS = [
    # {"code": "MAS", "name": "Chennai Central", "city": "Chennai", "state": "Tamil Nadu"},
    # Add more if needed, or leave empty
]

for s in NEW_STATIONS:
    exists = db.query(models.Station).filter(models.Station.code == s["code"]).first()
    if not exists:
        db.add(models.Station(**s))
        print(f"  + Station added: {s['code']} - {s['name']}")
    else:
        print(f"  = Station exists: {s['code']}")
db.commit()

# ─────────────────────────────────────────────────────────────────────────────
#  STEP 2: Define the train
# ─────────────────────────────────────────────────────────────────────────────
TRAIN_INFO = {
    "train_number": "12606",          # Unique train number (string)
    "name":         "Pallavan Sf Express (Return)",  # Full name
    "train_type":   "SF Express",     # Type label
}

# ─────────────────────────────────────────────────────────────────────────────
#  STEP 3: Define ticket classes & prices
# ─────────────────────────────────────────────────────────────────────────────
CLASSES = [
    {"code": "CC", "name": "Chair Car",     "price": 650},
    {"code": "2S", "name": "Second Seating","price": 180},
    # Add/remove as needed: 1A, 2A, 3A, SL, CC, 2S
]

# ─────────────────────────────────────────────────────────────────────────────
#  STEP 4: Define ALL stops in order (origin to terminus)
#
#  Fields:
#    station_code   : Station code (must exist in stations table)
#    arrival_time   : "HH:MM" string or None (None for first stop)
#    departure_time : "HH:MM" string or None (None for last stop)
#    distance_km    : Distance from origin in km (0 for first stop)
# ─────────────────────────────────────────────────────────────────────────────
STOPS = [
    # (station_code, arrival_time, departure_time, distance_km)
    ("KKDI", None,    "06:30",  0),
    ("PDKT", "07:30", "07:32",  62),
    ("TPJ",  "08:20", "08:25",  130),
    ("GOC",  "08:38", "08:39",  143),
    ("SRGM", "08:52", "08:54",  148),
    ("LLI",  "09:08", "09:09",  161),
    ("ALU",  "09:40", "09:41",  199),
    ("PNDM", "10:05", "10:06",  225),
    ("VRI",  "10:19", "10:21",  239),
    ("VM",   "11:02", "11:05",  305),
    ("MLMR", "12:07", "12:09",  375),
    ("CGL",  "12:32", "12:34",  405),
    ("TBM",  "13:00", "13:02",  433),
    ("MS",   "13:25", None,     455),
]

# ─────────────────────────────────────────────────────────────────────────────
#  STEP 5: Add train instances (dates the train runs on)
# ─────────────────────────────────────────────────────────────────────────────
JOURNEY_DATES = [
    date(2026, 5, 4),
    date(2026, 5, 5),
    date(2026, 5, 6),
    date(2026, 5, 7),
    date(2026, 5, 8),
    # Add more dates as needed
]

# ─────────────────────────────────────────────────────────────────────────────
#  AUTO-EXECUTION — Do not modify below this line
# ─────────────────────────────────────────────────────────────────────────────
def t(s):
    if s is None: return None
    h, m = map(int, s.split(":"))
    return time(h, m)

print(f"\nAdding train: {TRAIN_INFO['name']} ({TRAIN_INFO['train_number']})")

# Check if train already exists
train = db.query(models.Train).filter(models.Train.train_number == TRAIN_INFO["train_number"]).first()
if train:
    print(f"  = Train {TRAIN_INFO['train_number']} already exists, updating stops...")
    # Remove old stops
    db.query(models.TrainStop).filter(models.TrainStop.train_id == train.id).delete()
    db.commit()
else:
    train = models.Train(
        train_number=TRAIN_INFO["train_number"],
        name=TRAIN_INFO["name"],
        train_type=TRAIN_INFO.get("train_type", "Express")
    )
    db.add(train)
    db.flush()
    print(f"  + Train created with id={train.id}")

# Add classes
for cls_data in CLASSES:
    cls_master = db.query(models.ClassMaster).filter(models.ClassMaster.code == cls_data["code"]).first()
    if not cls_master:
        print(f"  ! ClassMaster '{cls_data['code']}' not found. Please add it to the DB first.")
        continue
    existing = db.query(models.TrainClass).filter(
        models.TrainClass.train_id == train.id,
        models.TrainClass.class_master_id == cls_master.id
    ).first()
    if not existing:
        db.add(models.TrainClass(train_id=train.id, class_master_id=cls_master.id, base_price=cls_data["price"]))
        print(f"  + Class added: {cls_data['code']} @ Rs.{cls_data['price']}")

# Add stops
for order, (code, arr, dep, dist) in enumerate(STOPS, start=1):
    station = db.query(models.Station).filter(models.Station.code == code).first()
    if not station:
        print(f"  ! Station '{code}' not found in DB. Please add it first.")
        continue
    db.add(models.TrainStop(
        train_id=train.id,
        station_id=station.id,
        stop_order=order,
        arrival_time=t(arr),
        departure_time=t(dep),
        distance_from_source=dist
    ))
    print(f"  + Stop {order}: {code} | arr={arr} dep={dep}")

# Add train instances (journey dates)
for jdate in JOURNEY_DATES:
    exists = db.query(models.TrainInstance).filter(
        models.TrainInstance.train_id == train.id,
        models.TrainInstance.journey_date == jdate
    ).first()
    if not exists:
        db.add(models.TrainInstance(train_id=train.id, journey_date=jdate))
        print(f"  + Instance: {jdate}")
    else:
        print(f"  = Instance already exists: {jdate}")

db.commit()
db.close()
print(f"\nDone! Train {TRAIN_INFO['train_number']} is now searchable.")
