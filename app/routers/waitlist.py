from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter()

@router.post("/waitlist", response_model=schemas.WaitlistResponse)
def join_waitlist(entry: schemas.WaitlistCreate, db: Session = Depends(get_db)):
    existing = db.query(models.WaitlistEntry).filter(
        models.WaitlistEntry.email == entry.email
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_entry = models.WaitlistEntry(email=entry.email)
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    return new_entry

@router.get("/waitlist/{id}", response_model=schemas.WaitlistResponse)
def get_entry(id: int, db: Session = Depends(get_db)):
    entry = db.query(models.WaitlistEntry).filter(
        models.WaitlistEntry.id == id
    ).first()
    
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    return entry