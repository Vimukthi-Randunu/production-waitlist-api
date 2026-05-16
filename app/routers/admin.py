from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from typing import List
import os

router = APIRouter()

def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=401, detail="Invalid API key")

@router.get("/admin/waitlist", response_model=List[schemas.WaitlistResponse])
def get_all_entries(db: Session = Depends(get_db), api_key: str = Depends(verify_api_key)):
    return db.query(models.WaitlistEntry).all()

@router.delete("/admin/waitlist/{id}")
def delete_entry(id: int, db: Session = Depends(get_db), api_key: str = Depends(verify_api_key)):
    entry = db.query(models.WaitlistEntry).filter(models.WaitlistEntry.id == id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    db.delete(entry)
    db.commit()
    return {"message": "Entry deleted"}