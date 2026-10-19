import json

from sqlalchemy.orm import Session

from app.models.summary import Summary
from app.schemas.summary import ActionItem, SummaryCreate


def get_summary_by_meeting_id(db: Session, meeting_id: str) -> Summary | None:
    """Retrieve a summary by meeting ID."""
    return db.query(Summary).filter(Summary.meeting_id == meeting_id).first()


def create_summary(db: Session, summary: SummaryCreate) -> Summary:
    """Create a new summary and return the Summary instance."""
    db_summary = Summary(
        meeting_id=summary.meeting_id,
        summary_text=summary.summary_text,
        action_items_json=json.dumps([item.model_dump() for item in summary.action_items]),
    )
    db.add(db_summary)
    db.commit()
    db.refresh(db_summary)
    return db_summary


def parse_action_items(summary: Summary) -> list[ActionItem]:
    raw = summary.action_items_json or "[]"
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []
    if not isinstance(data, list):
        return []
    items: list[ActionItem] = []
    for entry in data:
        if isinstance(entry, dict) and entry.get("task"):
            items.append(ActionItem(**entry))
    return items
