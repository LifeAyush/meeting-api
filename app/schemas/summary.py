from datetime import datetime
from pydantic import BaseModel


class SummaryCreate(BaseModel):
    meeting_id: str
    summary_text: str


class SummaryOut(SummaryCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
