from sqlalchemy.orm import Session

from app.models.summary import MeetingSummary
from app.schemas.summary import MeetingSummaryCreate

def get_summary_by_meeting_id(db: Session, meeting_id: str):
    return db.query(MeetingSummary).filter(MeetingSummary.meeting_id == meeting_id).first()

def create_summary(db: Session, summary: MeetingSummaryCreate):
    db_summary = MeetingSummary(**summary.model_dump())
    db.add(db_summary)
    db.commit()
    db.refresh(db_summary)
    return db_summary
