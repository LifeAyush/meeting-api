from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends

from app.db.session import get_db
from app.schemas.summary import MeetingSummaryOut
from app.services.summarizer import summarize_meeting

router = APIRouter()

@router.post("/{meeting_id}", response_model=MeetingSummaryOut)
def summarize(meeting_id: UUID, db: Session = Depends(get_db)):
    return summarize_meeting(db, str(meeting_id))
