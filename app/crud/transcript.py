from sqlalchemy.orm import Session

from app.models.transcript import Transcript
from app.schemas.transcript import TranscriptCreate

def create_transcript(db: Session, transcript: TranscriptCreate) -> Transcript:
    db_transcript = Transcript(**transcript.model_dump())
    db.add(db_transcript)
    db.commit()
    db.refresh(db_transcript)
    return db_transcript

def get_transcripts_by_meeting(db: Session, meeting_id: str):
    return db.query(Transcript).filter(Transcript.meeting_id == meeting_id).order_by(Transcript.timestamp).all()
