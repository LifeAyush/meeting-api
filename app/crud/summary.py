from sqlalchemy.orm import Session

from app.models.summary import Summary
from app.schemas.summary import SummaryCreate


def get_summary_by_meeting_id(db: Session, meeting_id: str) -> Summary | None:
    """Retrieve a summary by meeting ID."""
    return db.query(Summary).filter(Summary.meeting_id == meeting_id).first()


def create_summary(db: Session, summary: SummaryCreate) -> Summary:
    """Create a new summary and return the Summary instance."""
    db_summary = Summary(**summary.model_dump())
    db.add(db_summary)
    db.commit()
    db.refresh(db_summary)
    return db_summary
