import uuid
from sqlalchemy.orm import Session

from app.models.meeting import Meeting
from app.schemas.meeting import MeetingCreate

def create_meeting(db: Session, meeting_data: MeetingCreate) -> Meeting:
    meeting_id = str(uuid.uuid4())
    db_meeting = Meeting(id=meeting_id, title=meeting_data.title)
    db.add(db_meeting)
    db.commit()
    db.refresh(db_meeting)
    return db_meeting

def get_meeting(db: Session, meeting_id: str) -> Meeting:
    return db.query(Meeting).filter(Meeting.id == meeting_id).first()
