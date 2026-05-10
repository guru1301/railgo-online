from app.database import SessionLocal
from app import models

db = SessionLocal()
instances = db.query(models.TrainInstance).all()
if instances:
    dates = [i.journey_date for i in instances]
    print(f"Total instances: {len(instances)}")
    print(f"Min date: {min(dates)}")
    print(f"Max date: {max(dates)}")
    
    # Also print available stations
    stations = db.query(models.Station).all()
    print("Available Stations:")
    for s in stations:
        print(f" - {s.code}: {s.name} ({s.city})")

    # Also print available routes
    trains = db.query(models.Train).all()
    print("Available Routes:")
    for t in trains:
        print(f" - Train {t.train_number} ({t.name}): {t.source_station.code} to {t.destination_station.code}")
else:
    print("No train instances found.")
db.close()
