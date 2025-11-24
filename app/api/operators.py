from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas import OperatorCreate, OperatorUpdate, OperatorResponse
from app.services import OperatorService

router = APIRouter(prefix="/operators", tags=["operators"])


@router.post("", response_model=OperatorResponse, status_code=201)
def create_operator(
    operator_data: OperatorCreate,
    db: Session = Depends(get_db)
):
    operator = OperatorService.create_operator(db, operator_data)
    current_load = OperatorService.get_operator_current_load(db, operator.id)
    response = OperatorResponse(
        id=operator.id,
        name=operator.name,
        is_active=operator.is_active,
        max_load=operator.max_load,
        created_at=operator.created_at,
        current_load=current_load
    )
    return response


@router.get("", response_model=List[OperatorResponse])
def get_operators(db: Session = Depends(get_db)):
    operators = OperatorService.get_operators(db)
    response = []
    for operator in operators:
        current_load = OperatorService.get_operator_current_load(db, operator.id)
        response.append(OperatorResponse(
            id=operator.id,
            name=operator.name,
            is_active=operator.is_active,
            max_load=operator.max_load,
            created_at=operator.created_at,
            current_load=current_load
        ))
    return response


@router.patch("/{operator_id}", response_model=OperatorResponse)
def update_operator(
    operator_id: int,
    operator_data: OperatorUpdate,
    db: Session = Depends(get_db)
):
    operator = OperatorService.update_operator(db, operator_id, operator_data)
    if not operator:
        raise HTTPException(status_code=404, detail="Operator not found")

    current_load = OperatorService.get_operator_current_load(db, operator.id)
    response = OperatorResponse(
        id=operator.id,
        name=operator.name,
        is_active=operator.is_active,
        max_load=operator.max_load,
        created_at=operator.created_at,
        current_load=current_load
    )
    return response
