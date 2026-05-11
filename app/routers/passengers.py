from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from app import models, database, schemas
from app.security import get_current_user_id

router = APIRouter(prefix="/api/passengers", tags=["passengers"])


@router.get("", response_model=List[schemas.SavedPassenger])
def list_passengers(request: Request, db: Session = Depends(database.get_db)):
    """Return all saved passengers for the logged-in user."""
    user_id = get_current_user_id(request)
    return db.query(models.SavedPassenger).filter(
        models.SavedPassenger.user_id == user_id
    ).order_by(models.SavedPassenger.created_at.desc()).all()


@router.post("", response_model=schemas.SavedPassenger)
def add_passenger(req: schemas.SavedPassengerCreate, request: Request, db: Session = Depends(database.get_db)):
    """Add a new saved passenger for the logged-in user."""
    user_id = get_current_user_id(request)
    if not req.name.strip():
        raise HTTPException(status_code=400, detail="Name cannot be empty.")
    if not 1 <= req.age <= 120:
        raise HTTPException(status_code=400, detail="Age must be between 1 and 120.")
    p = models.SavedPassenger(
        user_id=user_id,
        name=req.name.strip(),
        age=req.age,
        gender=req.gender
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@router.put("/{passenger_id}", response_model=schemas.SavedPassenger)
def update_passenger(passenger_id: int, req: schemas.SavedPassengerUpdate, request: Request, db: Session = Depends(database.get_db)):
    """Update a saved passenger (must belong to the logged-in user)."""
    user_id = get_current_user_id(request)
    p = db.query(models.SavedPassenger).filter(
        models.SavedPassenger.id == passenger_id,
        models.SavedPassenger.user_id == user_id
    ).first()
    if not p:
        raise HTTPException(status_code=404, detail="Passenger not found.")
    p.name = req.name.strip()
    p.age = req.age
    p.gender = req.gender
    db.commit()
    db.refresh(p)
    return p


@router.delete("/{passenger_id}")
def delete_passenger(passenger_id: int, request: Request, db: Session = Depends(database.get_db)):
    """Delete a saved passenger (must belong to the logged-in user)."""
    user_id = get_current_user_id(request)
    p = db.query(models.SavedPassenger).filter(
        models.SavedPassenger.id == passenger_id,
        models.SavedPassenger.user_id == user_id
    ).first()
    if not p:
        raise HTTPException(status_code=404, detail="Passenger not found.")
    db.delete(p)
    db.commit()
    return {"success": True}
