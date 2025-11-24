from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List


class OperatorCreate(BaseModel):
    name: str = Field(..., min_length=1)
    is_active: bool = True
    max_load: int = Field(..., gt=0)


class OperatorUpdate(BaseModel):
    is_active: Optional[bool] = None
    max_load: Optional[int] = Field(None, gt=0)


class OperatorResponse(BaseModel):
    id: int
    name: str
    is_active: bool
    max_load: int
    created_at: datetime
    current_load: int

    class Config:
        from_attributes = True


class SourceCreate(BaseModel):
    name: str = Field(..., min_length=1)
    description: Optional[str] = None


class SourceResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class OperatorWeight(BaseModel):
    operator_id: int
    weight: float = Field(..., gt=0)


class SourceWeightsCreate(BaseModel):
    weights: List[OperatorWeight] = Field(..., min_length=1)


class ContactCreate(BaseModel):
    source_name: str = Field(..., min_length=1)
    external_id: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    name: Optional[str] = None
    message: Optional[str] = None

    @field_validator('external_id', 'phone', 'email')
    @classmethod
    def check_at_least_one_identifier(cls, v, info):
        if info.data.get('external_id') is None and info.data.get('phone') is None and info.data.get('email') is None and v is None:
            raise ValueError('At least one identifier (external_id, phone, or email) must be provided')
        return v


class ContactResponse(BaseModel):
    id: int
    lead_id: int
    source_id: int
    operator_id: Optional[int]
    status: str
    message: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ContactWithDetails(BaseModel):
    id: int
    status: str
    message: Optional[str]
    created_at: datetime
    source_name: str
    operator_name: Optional[str]

    class Config:
        from_attributes = True


class LeadResponse(BaseModel):
    id: int
    external_id: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    name: Optional[str]
    created_at: datetime
    contacts: List[ContactWithDetails]

    class Config:
        from_attributes = True


class StatisticsResponse(BaseModel):
    total_contacts: int
    total_leads: int
    contacts_with_operator: int
    contacts_without_operator: int
    operator_statistics: List[dict]
    source_statistics: List[dict]
