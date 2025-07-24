from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.session import get_db
from app.schemas.summary import SummaryOut
from app.services.summarizer import summarize_meeting


router = APIRouter()


def summary_api(meeting_id: UUID, db: Session = Depends(get_db)) -> SummaryOut:
    """Summarize a meeting and return the summary."""
    return summarize_meeting(db, str(meeting_id))
