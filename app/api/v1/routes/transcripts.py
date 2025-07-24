from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.crud.transcript import get_transcripts_by_meeting
from app.db.session import get_db
from app.schemas.transcript import TranscriptRead


router = APIRouter()


def transcripts_api(meeting_id: str, db: Session = Depends(get_db)) -> list[TranscriptRead]:
    """List all transcripts for a given meeting."""
    return get_transcripts_by_meeting(db, meeting_id)
