from __future__ import annotations

import json
import tempfile
from datetime import datetime

from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.core.whisper import transcribe_file
from app.crud.transcript import create_transcript
from app.db import session as db_session
from app.schemas.transcript import TranscriptCreate
from app.services.diarization import get_speaker_embeddings, match_speaker

active_connections: dict[str, list[WebSocket]] = {}
speaker_buffers: dict[str, dict[str, list]] = {}


async def websocket_endpoint(websocket: WebSocket, meeting_id: str) -> None:
    """WebSocket endpoint for real-time audio transcription and broadcasting."""
    await websocket.accept()

    if meeting_id not in active_connections:
        active_connections[meeting_id] = []
    active_connections[meeting_id].append(websocket)

    if meeting_id not in speaker_buffers:
        speaker_buffers[meeting_id] = {}

    try:
        while True:
            data = await websocket.receive_bytes()

            embedding = get_speaker_embeddings(data)
            matched_speaker = match_speaker(embedding, speaker_buffers[meeting_id])
            transcript_text = await transcribe_audio(data)

            db: Session = db_session.SessionLocal()
            try:
                new_transcript = create_transcript(
                    db,
                    TranscriptCreate(
                        meeting_id=meeting_id,
                        speaker=matched_speaker,
                        text=transcript_text,
                        timestamp=datetime.now(),
                    ),
                )
                payload = {
                    "id": new_transcript.id,
                    "meeting_id": meeting_id,
                    "speaker": matched_speaker,
                    "timestamp": new_transcript.timestamp.isoformat(),
                    "text": transcript_text,
                }
            finally:
                db.close()

            await broadcast(meeting_id, payload)

    except WebSocketDisconnect:
        connections = active_connections.get(meeting_id, [])
        if websocket in connections:
            connections.remove(websocket)


async def transcribe_audio(audio_bytes: bytes) -> str:
    """Transcribe audio bytes to text using Whisper."""
    with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
        tmp.write(audio_bytes)
        tmp.flush()
        return transcribe_file(tmp.name)


async def broadcast(meeting_id: str, message: dict) -> None:
    """Broadcast a message to all active WebSocket connections for a meeting."""
    for connection in list(active_connections.get(meeting_id, [])):
        await connection.send_text(json.dumps(message))
