from pydantic import BaseModel

class Nudge(BaseModel):
    """Schema for nudge output."""
    deal_id: str
    contact: str
    nudge: str
    urgency: int
    reply_speed: float
    tone: str