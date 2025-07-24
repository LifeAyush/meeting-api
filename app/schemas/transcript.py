from datetime import datetime
from pydantic import BaseModel


class TranscriptBase(BaseModel):
    speaker: str
    text: str
    timestamp: datetime


class TranscriptCreate(TranscriptBase):
    meeting_id: str


class TranscriptRead(TranscriptBase):
    id: int
    meeting_id: str

    class Config:
        from_attributes = True
