from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db, Base, engine
from ..models.item import Item
from ..schemas.item import ItemCreate, ItemOut
router = APIRouter(prefix="/items", tags=["items"])
Base.metadata.create_all(bind=engine)
@router.post("", response_model=ItemOut)
def create_item(payload: ItemCreate, db: Session = Depends(get_db)):
    obj = Item(name=payload.name, description=payload.description)
    db.add(obj); db.commit(); db.refresh(obj); return obj
@router.get("", response_model=List[ItemOut])
def list_items(db: Session = Depends(get_db), page: int = 1, per_page: int = 20):
    page = max(1, page); per_page = min(max(1, per_page), 100)
    return db.query(Item).order_by(Item.id.asc()).offset((page-1)*per_page).limit(per_page).all()
@router.get("/{item_id}", response_model=ItemOut)
def get_item(item_id: int, db: Session = Depends(get_db)):
    obj = db.get(Item, item_id)
    if not obj: raise HTTPException(404, "Item not found")
    return obj
@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    obj = db.get(Item, item_id)
    if not obj: raise HTTPException(404, "Item not found")
    db.delete(obj); db.commit(); return