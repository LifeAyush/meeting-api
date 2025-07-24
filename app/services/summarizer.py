import openai

from app.crud.summary import create_summary, get_summary_by_meeting_id
from app.crud.transcript import get_transcripts_by_meeting
from app.schemas.summary import SummaryCreate
from sqlalchemy.orm import Session


def summarize_meeting(db: Session, meeting_id: str) -> dict:
    """Summarize a meeting's transcript using OpenAI and store the summary."""
    existing = get_summary_by_meeting_id(db, meeting_id)
    if existing:
        return existing

    transcripts = get_transcripts_by_meeting(db, meeting_id)
    full_text = "\n".join([f"{t.speaker}: {t.text}" for t in transcripts])

    prompt = f"Summarize the following meeting transcript:\n\n{full_text}\n\nSummary:"

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
    )

    summary_text = response.choices[0].message["content"].strip()
    return create_summary(
        db,
        SummaryCreate(meeting_id=meeting_id, summary_text=summary_text)
    )
