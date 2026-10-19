from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TranscriptBase(BaseModel):
    speaker: str
    text: str
    timestamp: datetime


class TranscriptCreate(TranscriptBase):
    meeting_id: str


class TranscriptRead(TranscriptBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    meeting_id: str
