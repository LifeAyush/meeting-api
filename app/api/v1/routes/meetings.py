from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud.meeting import create_meeting, get_meeting
from app.db.session import get_db
from app.schemas.meeting import MeetingCreate, MeetingOut


router = APIRouter()


def create_meeting_api(meeting: MeetingCreate, db: Session = Depends(get_db)) -> MeetingOut:
    """Create a new meeting and return its details."""
    return create_meeting(db, meeting)


def get_meeting_api(meeting_id: str, db: Session = Depends(get_db)) -> MeetingOut:
    """Retrieve a meeting by its ID or raise 404 if not found."""
    meeting = get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting
