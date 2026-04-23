from sqlalchemy import Column, Integer, String, DateTime, Enum, func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class HCPSpecialty(str, enum.Enum):
    oncologist       = "Oncologist"
    cardiologist     = "Cardiologist"
    neurologist      = "Neurologist"
    general_practice = "General Practice"
    psychiatrist     = "Psychiatrist"
    diabetologist    = "Diabetologist"
    pulmonologist    = "Pulmonologist"
    other            = "Other"


class HCP(Base):
    __tablename__ = "hcps"

    id           = Column(Integer, primary_key=True, index=True)
    full_name    = Column(String(150), nullable=False, index=True)
    specialty    = Column(Enum(HCPSpecialty), nullable=True)
    institution  = Column(String(200), nullable=True)
    city         = Column(String(100), nullable=True)
    email        = Column(String(120), nullable=True)
    phone        = Column(String(30), nullable=True)
    created_at   = Column(DateTime, server_default=func.now())

    interactions = relationship("Interaction", back_populates="hcp")