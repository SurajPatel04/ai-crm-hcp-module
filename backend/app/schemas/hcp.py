from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class HCPCreate(BaseModel):
    full_name: str
    specialty: Optional[str] = None
    institution: Optional[str] = None
    city: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None


class HCPUpdate(BaseModel):
    full_name: Optional[str] = None
    specialty: Optional[str] = None
    institution: Optional[str] = None
    city: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None


class HCPResponse(BaseModel):
    id: int
    full_name: str
    specialty: Optional[str] = None
    institution: Optional[str] = None
    city: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
