import json
import numpy as np
import tempfile
import whisper
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from uuid import uuid4

from app.crud.transcript import create_transcript
from app.db.session import get_db
from app.schemas.transcript import TranscriptCreate
from app.services.diarization import get_speaker_embeddings


model = whisper.load_model("base")
active_connections = {}
speaker_buffers = {}


async def websocket_endpoint(websocket: WebSocket, meeting_id: str) -> None:
    """WebSocket endpoint for real-time audio transcription and broadcasting."""
    await websocket.accept()

    if meeting_id not in active_connections:
        active_connections[meeting_id] = []
    active_connections[meeting_id].append(websocket)

    try:
        while True:
            data = await websocket.receive_bytes()

            speaker_embedding = get_speaker_embeddings(data)
            matched_speaker = None
            for speaker_id, emb_list in speaker_buffers.items():
                sim = np.inner(speaker_embedding, np.mean(emb_list, axis=0))
                if sim > 0.75:  # Adjustable threshold
                    matched_speaker = speaker_id
                    speaker_buffers[speaker_id].append(speaker_embedding)
                    break

            if not matched_speaker:
                matched_speaker = str(uuid4())[:8]
                speaker_buffers[matched_speaker] = [speaker_embedding]

            transcript_text = await transcribe_audio(data)

            db: Session = next(get_db())
            new_transcript = create_transcript(
                db,
                TranscriptCreate(
                    meeting_id=meeting_id,
                    speaker=matched_speaker,
                    text=transcript_text,
                    timestamp=datetime.now()
                )
            )

            # Broadcast to all clients
            payload = {
                "id": new_transcript.id,
                "meeting_id": meeting_id,
                "speaker": matched_speaker,
                "timestamp": new_transcript.timestamp.isoformat(),
                "text": transcript_text
            }

            await broadcast(meeting_id, payload)

    except WebSocketDisconnect:
        active_connections[meeting_id].remove(websocket)


async def transcribe_audio(audio_bytes: bytes) -> str:
    """Transcribe audio bytes to text using the Whisper model."""
    with tempfile.NamedTemporaryFile(suffix=".wav") as f:
        f.write(audio_bytes)
        f.flush()
        result = model.transcribe(f.name)
        text = result["text"]

    return text.strip()


async def broadcast(meeting_id: str, message: dict) -> None:
    """Broadcast a message to all active WebSocket connections for a meeting."""
    for connection in active_connections.get(meeting_id, []):
        await connection.send_text(json.dumps(message))
