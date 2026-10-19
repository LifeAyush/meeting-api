from __future__ import annotations

import json
import re

from sqlalchemy.orm import Session

from app.core.config import openai_api_key, summary_mode
from app.crud.summary import create_summary, get_summary_by_meeting_id, parse_action_items
from app.crud.transcript import get_transcripts_by_meeting
from app.schemas.summary import ActionItem, SummaryCreate, SummaryOut


def summary_to_out(summary) -> SummaryOut:
    return SummaryOut(
        id=summary.id,
        meeting_id=summary.meeting_id,
        summary_text=summary.summary_text,
        action_items=parse_action_items(summary),
        created_at=summary.created_at,
    )


def summarize_meeting(db: Session, meeting_id: str) -> SummaryOut:
    """Summarize a meeting's transcripts and store summary + action items."""
    existing = get_summary_by_meeting_id(db, meeting_id)
    if existing:
        return summary_to_out(existing)

    transcripts = get_transcripts_by_meeting(db, meeting_id)
    full_text = "\n".join(f"{t.speaker}: {t.text}" for t in transcripts)

    if summary_mode() == "openai" and openai_api_key():
        summary_text, action_items = _summarize_with_openai(full_text)
    else:
        summary_text, action_items = _summarize_mock(full_text, transcripts)

    created = create_summary(
        db,
        SummaryCreate(
            meeting_id=meeting_id,
            summary_text=summary_text,
            action_items=action_items,
        ),
    )
    return summary_to_out(created)


def _summarize_mock(full_text: str, transcripts) -> tuple[str, list[ActionItem]]:
    if not transcripts:
        return (
            "No transcript content was available for this meeting.",
            [],
        )
    speakers = sorted({t.speaker for t in transcripts})
    preview = full_text[:400].strip() or "(empty)"
    summary_text = (
        f"Mock summary for {len(transcripts)} transcript segment(s) "
        f"from speaker(s) {', '.join(speakers)}. Preview: {preview}"
    )
    action_items = [
        ActionItem(
            owner=speakers[0] if speakers else "team",
            task="Review the transcript and confirm next steps",
            due_hint="this week",
        )
    ]
    return summary_text, action_items


def _summarize_with_openai(full_text: str) -> tuple[str, list[ActionItem]]:
    from openai import OpenAI

    client = OpenAI(api_key=openai_api_key())
    prompt = (
        "Summarize the meeting transcript and extract action items. "
        "Respond with JSON only in this shape:\n"
        '{"summary_text":"...","action_items":[{"owner":"","task":"...","due_hint":null}]}\n\n'
        f"Transcript:\n{full_text}"
    )
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    content = (response.choices[0].message.content or "").strip()
    parsed = _parse_json_object(content)
    summary_text = str(parsed.get("summary_text") or content)
    raw_items = parsed.get("action_items") or []
    action_items: list[ActionItem] = []
    if isinstance(raw_items, list):
        for entry in raw_items:
            if isinstance(entry, dict) and entry.get("task"):
                action_items.append(
                    ActionItem(
                        owner=str(entry.get("owner") or ""),
                        task=str(entry["task"]),
                        due_hint=entry.get("due_hint"),
                    )
                )
    return summary_text, action_items


def _parse_json_object(content: str) -> dict:
    try:
        data = json.loads(content)
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if not match:
            return {}
        try:
            data = json.loads(match.group(0))
            return data if isinstance(data, dict) else {}
        except json.JSONDecodeError:
            return {}
