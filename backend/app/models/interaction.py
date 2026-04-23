from sqlalchemy import (
    Column, Integer, String, Text, Date, Time,
    DateTime, ForeignKey, Enum, func
)
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

class InteractionType(str, enum.Enum):
    meeting    = "Meeting"
    call       = "Call"
    email      = "Email"
    conference = "Conference"
    virtual    = "Virtual"


class SentimentType(str, enum.Enum):
    positive = "Positive"
    neutral  = "Neutral"
    negative = "Negative"


class Interaction(Base):
    __tablename__ = "interactions"

    id                  = Column(Integer, primary_key=True, index=True)
    hcp_id              = Column(Integer, ForeignKey("hcps.id"), nullable=False)
    logged_by_user_id   = Column(Integer, ForeignKey("users.id"), nullable=False)

    interaction_type    = Column(Enum(InteractionType), nullable=False, default=InteractionType.meeting)
    interaction_date    = Column(Date, nullable=False)
    interaction_time    = Column(Time, nullable=True)
    topics_discussed    = Column(Text, nullable=True)
    sentiment           = Column(Enum(SentimentType), nullable=True, default=SentimentType.neutral)
    outcomes            = Column(Text, nullable=True)
    log_method          = Column(String(10), nullable=False, default="form")

    ai_summary          = Column(Text, nullable=True)
    raw_chat_input      = Column(Text, nullable=True)

    created_at          = Column(DateTime, server_default=func.now())
    updated_at          = Column(DateTime, server_default=func.now(), onupdate=func.now())

    hcp            = relationship("HCP",  back_populates="interactions")
    logged_by_user = relationship("User", back_populates="interactions")

    @property
    def hcp_name(self) -> str | None:
        return self.hcp.full_name if self.hcp else None
