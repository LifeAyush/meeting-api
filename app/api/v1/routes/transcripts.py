from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.transcript import TranscriptRead
from app.crud.transcript import get_transcripts_by_meeting

router = APIRouter()

@router.get("/{meeting_id}", response_model=list[TranscriptRead])
def list_transcripts(meeting_id: str, db: Session = Depends(get_db)):
    return get_transcripts_by_meeting(db, meeting_id)
