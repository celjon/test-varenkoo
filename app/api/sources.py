from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import SourceCreate, SourceResponse, SourceWeightsCreate
from app.services import SourceService

router = APIRouter(prefix="/sources", tags=["sources"])


@router.post("", response_model=SourceResponse, status_code=201)
def create_source(
    source_data: SourceCreate,
    db: Session = Depends(get_db)
):
    existing_source = SourceService.get_source_by_name(db, source_data.name)
    if existing_source:
        raise HTTPException(status_code=400, detail="Source with this name already exists")

    source = SourceService.create_source(db, source_data)
    return source


@router.post("/{source_id}/weights", status_code=200)
def set_source_weights(
    source_id: int,
    weights_data: SourceWeightsCreate,
    db: Session = Depends(get_db)
):
    success = SourceService.set_operator_weights(db, source_id, weights_data)
    if not success:
        raise HTTPException(status_code=404, detail="Source or operator not found")

    return {"message": "Weights updated successfully"}
