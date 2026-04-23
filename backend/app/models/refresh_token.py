from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean,
    ForeignKey, func
)
from sqlalchemy.orm import relationship
from app.core.database import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    token = Column(String, unique=True, nullable=False)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    user = relationship(
        "User",
        back_populates="refresh_tokens"
    )

    device_info = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)

    expires_at = Column(DateTime, nullable=False)

    is_revoked = Column(Boolean, default=False)

    created_at = Column(DateTime, server_default=func.now())