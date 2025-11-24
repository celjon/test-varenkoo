from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import ContactCreate, ContactResponse
from app.services import ContactService

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.post("", response_model=ContactResponse, status_code=201)
def create_contact(
    contact_data: ContactCreate,
    db: Session = Depends(get_db)
):
    try:
        contact = ContactService.create_contact(db, contact_data)
        return contact
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
