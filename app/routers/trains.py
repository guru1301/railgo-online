from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app import crud, schemas, database, models
from fastapi_cache.decorator import cache
import os
import requests as http_requests

router = APIRouter(prefix="/api/trains", tags=["trains"])

@router.get("/search")
@cache(expire=60)
def search_trains(
    source: str = Query(...),
    destination: str = Query(...),
    date_val: date = Query(..., alias="date"),
    classType: Optional[str] = Query(None),
    db: Session = Depends(database.get_db)
):
    search_results = crud.search_trains(db, source_code=source.upper(), destination_code=destination.upper(), journey_date=date_val)
    if not search_results:
        return []
    
    results = []
    for instance, source_stop, dest_stop in search_results:
        train = instance.train
        for tc in train.train_classes:
            if classType and tc.class_master.code != classType:
                continue
                
            results.append({
                "trainNumber": train.train_number,
                "name": train.name,
                "departureTime": source_stop.departure_time.strftime("%H:%M"),
                "arrivalTime": dest_stop.arrival_time.strftime("%H:%M"),
                "source": source_stop.station.code,
                "destination": dest_stop.station.code,
                "classType": tc.class_master.code,
                "date": instance.journey_date.isoformat(),
                "price": tc.base_price
            })
            
    return results

@router.get("/stations", response_model=List[schemas.Station])
@cache(expire=300)
def get_stations(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    return crud.get_stations(db, skip=skip, limit=limit)

@router.get("/{train_number}/schedule")
def get_train_schedule(train_number: str, db: Session = Depends(database.get_db)):
    stops = crud.get_train_schedule(db, train_number)
    if not stops:
        raise HTTPException(status_code=404, detail="Train not found")
        
    results = []
    for stop in stops:
        results.append({
            "stationCode": stop.station.code,
            "stationName": stop.station.name,
            "arrivalTime": stop.arrival_time.strftime("%H:%M") if stop.arrival_time else None,
            "departureTime": stop.departure_time.strftime("%H:%M") if stop.departure_time else None,
            "day": 1,
            "distance": stop.distance_from_source
        })
    return results

@router.get("/live-status")
def get_live_status(trainNo: str, startDay: str = "0"):
    API_KEY = os.getenv("RAPIDAPI_KEY")
    API_HOST = os.getenv("RAPIDAPI_HOST", "irctc1.p.rapidapi.com")

    if not API_KEY:
        raise HTTPException(status_code=500, detail="RapidAPI key not configured")

    try:
        response = http_requests.get(
            f"https://{API_HOST}/api/v1/liveTrainStatus",
            params={"trainNo": trainNo, "startDay": startDay},
            headers={
                "X-RapidAPI-Key": API_KEY,
                "X-RapidAPI-Host": API_HOST
            },
            timeout=15
        )
        data = response.json()
        if response.status_code != 200 or data.get("status") is False:
            raise HTTPException(status_code=502, detail=data.get("message", "Failed to fetch from RapidAPI"))
        return data
    except http_requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Could not reach RapidAPI: {str(e)}")
