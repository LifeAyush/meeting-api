from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

class MeetingSummaryCreate(BaseModel):
    meeting_id: UUID
    summary_text: str

class MeetingSummaryOut(MeetingSummaryCreate):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
