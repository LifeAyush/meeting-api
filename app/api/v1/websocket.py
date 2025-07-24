import json
import whisper
import tempfile
import numpy as np
from uuid import uuid4
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import WebSocket, WebSocketDisconnect

from app.db.session import get_db
from app.crud.transcript import create_transcript
from app.services.diarization import get_speaker_embeddings
from app.schemas.transcript import TranscriptCreate

model = whisper.load_model("base")
active_connections = {}
speaker_buffers = {}

async def websocket_endpoint(websocket: WebSocket, meeting_id: str):
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

async def transcribe_audio(audio_bytes: bytes):
    # Write audio to a temporary WAV file
    with tempfile.NamedTemporaryFile(suffix=".wav") as f:
        f.write(audio_bytes)
        f.flush()
        result = model.transcribe(f.name)
        text = result["text"]

    return text.strip()

async def broadcast(meeting_id: str, message: dict):
    for connection in active_connections.get(meeting_id, []):
        await connection.send_text(json.dumps(message))
