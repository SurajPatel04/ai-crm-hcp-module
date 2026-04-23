from pydantic import BaseModel
from typing import Optional
from datetime import date, time, datetime


class InteractionCreate(BaseModel):
    hcp_id: int
    interaction_type: str = "Meeting"
    interaction_date: date
    interaction_time: Optional[time] = None
    topics_discussed: Optional[str] = None
    sentiment: Optional[str] = "Neutral"
    outcomes: Optional[str] = None
    log_method: str = "form"
    ai_summary: Optional[str] = None
    raw_chat_input: Optional[str] = None


class InteractionUpdate(BaseModel):
    hcp_id: Optional[int] = None
    interaction_type: Optional[str] = None
    interaction_date: Optional[date] = None
    interaction_time: Optional[time] = None
    topics_discussed: Optional[str] = None
    sentiment: Optional[str] = None
    outcomes: Optional[str] = None
    log_method: Optional[str] = None
    ai_summary: Optional[str] = None
    raw_chat_input: Optional[str] = None


class InteractionResponse(BaseModel):
    id: int
    hcp_id: int
    hcp_name: Optional[str] = None
    logged_by_user_id: int
    interaction_type: Optional[str] = None
    interaction_date: Optional[date] = None
    interaction_time: Optional[time] = None
    topics_discussed: Optional[str] = None
    sentiment: Optional[str] = None
    outcomes: Optional[str] = None
    log_method: Optional[str] = None
    ai_summary: Optional[str] = None
    raw_chat_input: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
