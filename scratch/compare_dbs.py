import os
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import sys

# Add parent dir to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import models

def compare_dbs():
    load_dotenv()
    
    # Supabase Connection
    supabase_url = os.environ.get("DATABASE_URL")
    if not supabase_url:
        print("Error: DATABASE_URL not found in .env")
        return
    
    # SQLite Connection
    sqlite_url = "sqlite:///./railgo.db"
    
    try:
        engine_sp = create_engine(supabase_url)
        engine_sq = create_engine(sqlite_url)
        
        SessionSP = sessionmaker(bind=engine_sp)
        SessionSQ = sessionmaker(bind=engine_sq)
        
        db_sp = SessionSP()
        db_sq = SessionSQ()
        
        tables = [
            models.Station,
            models.ClassMaster,
            models.Train,
            models.TrainClass,
            models.TrainInstance,
            models.TrainStop,
            models.User,
            models.Booking,
            models.Passenger
        ]
        
        print(f"{'Table':<20} | {'SQLite Count':<12} | {'Supabase Count':<15} | {'Match'}")
        print("-" * 60)
        
        all_match = True
        for table in tables:
            name = table.__tablename__
            try:
                count_sq = db_sq.query(table).count()
            except Exception:
                count_sq = "Error/Missing"
                
            try:
                count_sp = db_sp.query(table).count()
            except Exception:
                count_sp = "Error/Missing"
            
            match = "[OK]" if count_sq == count_sp and count_sq != "Error/Missing" else "[DIFF]"
            if match == "[DIFF]":
                all_match = False
            
            print(f"{name:<20} | {str(count_sq):<12} | {str(count_sp):<15} | {match}")
            
        print("-" * 60)
        if all_match:
            print("Summary: All table counts match perfectly!")
        else:
            print("Summary: There are differences in table counts between SQLite and Supabase.")
            
        db_sp.close()
        db_sq.close()
        
    except Exception as e:
        print(f"Comparison failed: {e}")

if __name__ == "__main__":
    compare_dbs()
