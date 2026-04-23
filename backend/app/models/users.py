from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from app.core.database import Base
 
 
class User(Base):
    __tablename__ = "users"
 
    id              = Column(Integer, primary_key=True, index=True)
    full_name       = Column(String(120), nullable=False)
    email           = Column(String(120), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active       = Column(Boolean, default=True)
    role            = Column(String(50), default="user")
    created_at      = Column(DateTime, server_default=func.now())
    updated_at      = Column(DateTime, server_default=func.now(), onupdate=func.now())
 
    interactions    = relationship("Interaction", back_populates="logged_by_user")
    refresh_tokens  = relationship("RefreshToken", back_populates="user")
 