from sqlalchemy.orm import Session
from sqlalchemy import func, case
from app.models import Operator, Source, Lead, Contact, OperatorSourceWeight
from app.schemas import (
    OperatorCreate, OperatorUpdate, SourceCreate,
    ContactCreate, SourceWeightsCreate
)
from typing import Optional, List
import random


class OperatorService:
    @staticmethod
    def create_operator(db: Session, operator_data: OperatorCreate) -> Operator:
        operator = Operator(**operator_data.model_dump())
        db.add(operator)
        db.commit()
        db.refresh(operator)
        return operator

    @staticmethod
    def get_operators(db: Session) -> List[Operator]:
        return db.query(Operator).all()

    @staticmethod
    def get_operator(db: Session, operator_id: int) -> Optional[Operator]:
        return db.query(Operator).filter(Operator.id == operator_id).first()

    @staticmethod
    def update_operator(db: Session, operator_id: int, operator_data: OperatorUpdate) -> Optional[Operator]:
        operator = db.query(Operator).filter(Operator.id == operator_id).first()
        if not operator:
            return None

        update_data = operator_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(operator, field, value)

        db.commit()
        db.refresh(operator)
        return operator

    @staticmethod
    def get_operator_current_load(db: Session, operator_id: int) -> int:
        return db.query(Contact).filter(
            Contact.operator_id == operator_id,
            Contact.status != 'closed'
        ).count()


class SourceService:
    @staticmethod
    def create_source(db: Session, source_data: SourceCreate) -> Source:
        source = Source(**source_data.model_dump())
        db.add(source)
        db.commit()
        db.refresh(source)
        return source

    @staticmethod
    def get_source_by_name(db: Session, name: str) -> Optional[Source]:
        return db.query(Source).filter(Source.name == name).first()

    @staticmethod
    def set_operator_weights(db: Session, source_id: int, weights_data: SourceWeightsCreate) -> bool:
        source = db.query(Source).filter(Source.id == source_id).first()
        if not source:
            return False

        db.query(OperatorSourceWeight).filter(
            OperatorSourceWeight.source_id == source_id
        ).delete()

        for weight_item in weights_data.weights:
            operator = db.query(Operator).filter(Operator.id == weight_item.operator_id).first()
            if not operator:
                db.rollback()
                return False

            weight_record = OperatorSourceWeight(
                operator_id=weight_item.operator_id,
                source_id=source_id,
                weight=weight_item.weight
            )
            db.add(weight_record)

        db.commit()
        return True


class LeadService:
    @staticmethod
    def find_or_create_lead(db: Session, contact_data: ContactCreate) -> Lead:
        lead = None

        if contact_data.external_id:
            lead = db.query(Lead).filter(Lead.external_id == contact_data.external_id).first()

        if not lead and contact_data.phone:
            lead = db.query(Lead).filter(Lead.phone == contact_data.phone).first()

        if not lead and contact_data.email:
            lead = db.query(Lead).filter(Lead.email == contact_data.email).first()

        if not lead:
            lead = Lead(
                external_id=contact_data.external_id,
                phone=contact_data.phone,
                email=contact_data.email,
                name=contact_data.name
            )
            db.add(lead)
            db.commit()
            db.refresh(lead)
        else:
            if contact_data.external_id and not lead.external_id:
                lead.external_id = contact_data.external_id
            if contact_data.phone and not lead.phone:
                lead.phone = contact_data.phone
            if contact_data.email and not lead.email:
                lead.email = contact_data.email
            if contact_data.name and not lead.name:
                lead.name = contact_data.name
            db.commit()
            db.refresh(lead)

        return lead

    @staticmethod
    def get_leads(db: Session) -> List[Lead]:
        return db.query(Lead).all()


class ContactService:
    @staticmethod
    def select_operator(db: Session, source_id: int) -> Optional[Operator]:
        weights = db.query(OperatorSourceWeight).filter(
            OperatorSourceWeight.source_id == source_id
        ).all()

        if not weights:
            return None

        eligible_operators = []
        for weight_record in weights:
            operator = weight_record.operator
            if not operator.is_active:
                continue

            current_load = OperatorService.get_operator_current_load(db, operator.id)
            if current_load >= operator.max_load:
                continue

            eligible_operators.append((operator, weight_record.weight))

        if not eligible_operators:
            return None

        total_weight = sum(weight for _, weight in eligible_operators)
        random_value = random.uniform(0, total_weight)

        cumulative_weight = 0
        for operator, weight in eligible_operators:
            cumulative_weight += weight
            if random_value <= cumulative_weight:
                return operator

        return eligible_operators[-1][0]

    @staticmethod
    def create_contact(db: Session, contact_data: ContactCreate) -> Contact:
        source = SourceService.get_source_by_name(db, contact_data.source_name)
        if not source:
            raise ValueError(f"Source '{contact_data.source_name}' not found")

        lead = LeadService.find_or_create_lead(db, contact_data)

        operator = ContactService.select_operator(db, source.id)

        contact = Contact(
            lead_id=lead.id,
            source_id=source.id,
            operator_id=operator.id if operator else None,
            message=contact_data.message,
            status='new'
        )
        db.add(contact)
        db.commit()
        db.refresh(contact)
        return contact


class StatisticsService:
    @staticmethod
    def get_statistics(db: Session) -> dict:
        total_contacts = db.query(Contact).count()
        total_leads = db.query(Lead).count()
        contacts_with_operator = db.query(Contact).filter(Contact.operator_id.isnot(None)).count()
        contacts_without_operator = db.query(Contact).filter(Contact.operator_id.is_(None)).count()

        operator_stats = db.query(
            Operator.id,
            Operator.name,
            Operator.is_active,
            Operator.max_load,
            func.count(Contact.id).label('total_contacts'),
            func.sum(case((Contact.status != 'closed', 1), else_=0)).label('active_contacts')
        ).outerjoin(Contact, Operator.id == Contact.operator_id).group_by(Operator.id).all()

        operator_statistics = [
            {
                'operator_id': stat.id,
                'operator_name': stat.name,
                'is_active': stat.is_active,
                'max_load': stat.max_load,
                'current_load': stat.active_contacts or 0,
                'total_contacts': stat.total_contacts
            }
            for stat in operator_stats
        ]

        source_stats = db.query(
            Source.id,
            Source.name,
            func.count(Contact.id).label('total_contacts')
        ).outerjoin(Contact, Source.id == Contact.source_id).group_by(Source.id).all()

        source_statistics = [
            {
                'source_id': stat.id,
                'source_name': stat.name,
                'total_contacts': stat.total_contacts
            }
            for stat in source_stats
        ]

        return {
            'total_contacts': total_contacts,
            'total_leads': total_leads,
            'contacts_with_operator': contacts_with_operator,
            'contacts_without_operator': contacts_without_operator,
            'operator_statistics': operator_statistics,
            'source_statistics': source_statistics
        }
