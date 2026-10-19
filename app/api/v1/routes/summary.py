from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.summary import SummaryOut
from app.services.summarizer import summarize_meeting

router = APIRouter()


@router.post("/{meeting_id}", response_model=SummaryOut)
def summary_api(meeting_id: UUID, db: Session = Depends(get_db)) -> SummaryOut:
    """Summarize a meeting and return the summary plus action items."""
    return summarize_meeting(db, str(meeting_id))


@router.get("/{meeting_id}", response_model=SummaryOut)
def get_summary_api(meeting_id: UUID, db: Session = Depends(get_db)) -> SummaryOut:
    """Return an existing summary for a meeting (creates none)."""
    from fastapi import HTTPException

    from app.crud.summary import get_summary_by_meeting_id
    from app.services.summarizer import summary_to_out

    existing = get_summary_by_meeting_id(db, str(meeting_id))
    if not existing:
        raise HTTPException(status_code=404, detail="Summary not found")
    return summary_to_out(existing)
