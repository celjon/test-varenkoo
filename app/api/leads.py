from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas import LeadResponse, ContactWithDetails
from app.services import LeadService, StatisticsService

router = APIRouter(prefix="/leads", tags=["leads"])


@router.get("", response_model=List[LeadResponse])
def get_leads(db: Session = Depends(get_db)):
    leads = LeadService.get_leads(db)
    response = []
    for lead in leads:
        contacts = []
        for contact in lead.contacts:
            contacts.append(ContactWithDetails(
                id=contact.id,
                status=contact.status,
                message=contact.message,
                created_at=contact.created_at,
                source_name=contact.source.name,
                operator_name=contact.operator.name if contact.operator else None
            ))

        response.append(LeadResponse(
            id=lead.id,
            external_id=lead.external_id,
            phone=lead.phone,
            email=lead.email,
            name=lead.name,
            created_at=lead.created_at,
            contacts=contacts
        ))
    return response


@router.get("/statistics")
def get_statistics(db: Session = Depends(get_db)):
    return StatisticsService.get_statistics(db)
