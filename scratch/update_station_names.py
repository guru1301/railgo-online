import os
import sys

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app import models

db = SessionLocal()

station_names = {
    "MS": "Chennai Egmore",
    "KKDI": "Karaikkudi Jn",
    "TBM": "Tambaram",
    "CGL": "Chengalpattu Jn",
    "MLMR": "Melmaruvathur",
    "VM": "Villupuram Jn",
    "VRI": "Vriddhachalam Jn",
    "PNDM": "Pennadam",
    "ALU": "Ariyalur",
    "LLI": "Lalgudi",
    "SRGM": "Srirangam",
    "GOC": "Ponmalai (Golden Rock)",
    "TPJ": "Tiruchchirappalli Jn",
    "PDKT": "Pudukkottai",
    "MDU": "Madurai Jn",
    "MPA": "Manaparai",
    "DG": "Dindigul Jn",
    "SDN": "Sholavandan",
    "KON": "Kudalnagar",
    "MBM": "Mambalam",
    "TMV": "Tindivanam",
    "PRT": "Panruti",
    "TDPR": "Tirupadripulyur",
    "CUPJ": "Cuddalore Port Jn",
    "CDM": "Chidambaram",
    "SY": "Sirkazhi",
    "VDL": "Vaitisvarankoil",
    "MV": "Mayiladuturai Jn",
    "ADT": "Aduturai",
    "KMU": "Kumbakonam",
    "PML": "Papanasam",
    "TJ": "Thanjavur Jn",
    "BAL": "Budalur",
    "TRB": "Tiruverumbur",
    "NDLS": "New Delhi",
    "MMCT": "Mumbai Central",
    "MAS": "Chennai Central",
    "HWH": "Howrah Junction"
}

def update_station_names():
    print("Updating station names in database...")
    count = 0
    for code, name in station_names.items():
        station = db.query(models.Station).filter(models.Station.code == code).first()
        if station:
            station.name = name
            station.city = name.replace(" Jn", "").replace(" Central", "").replace(" Junction", "")
            count += 1
    
    db.commit()
    print(f"Successfully updated {count} station names!")

if __name__ == "__main__":
    update_station_names()
    db.close()
