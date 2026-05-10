from fastapi import APIRouter, HTTPException
import random
from fastapi_cache.decorator import cache

router = APIRouter(prefix="/api/train-tracking", tags=["tracking"])

@router.get("/track/{train_number}")
@cache(expire=20)
def track_train(train_number: str):
    if len(train_number) != 5:
        raise HTTPException(status_code=400, detail="Invalid train number")
    
    # Mock response for tracking
    return {
        "success": True,
        "data": {
            "train_number": train_number,
            "status": "Running",
            "current_station": "Station " + str(random.randint(1, 10)),
            "delay_minutes": random.randint(0, 120),
            "last_updated": "Just now"
        }
    }
