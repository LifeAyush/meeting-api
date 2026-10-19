from __future__ import annotations

import json
import math
import struct
import wave
from io import BytesIO


def _sine_wav_bytes(duration_s: float = 0.25, sample_rate: int = 16_000) -> bytes:
    buffer = BytesIO()
    n_frames = int(sample_rate * duration_s)
    with wave.open(buffer, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        frames = bytearray()
        for i in range(n_frames):
            value = int(0.2 * 32767 * math.sin(2 * math.pi * 440 * i / sample_rate))
            frames.extend(struct.pack("<h", value))
        wf.writeframes(frames)
    return buffer.getvalue()


def test_websocket_transcript_and_mock_summary(client):
    meeting = client.post("/api/v1/meetings/", json={"title": "WS demo"}).json()
    meeting_id = meeting["id"]

    with client.websocket_connect(f"/ws/meetings/{meeting_id}") as websocket:
        websocket.send_bytes(_sine_wav_bytes())
        message = json.loads(websocket.receive_text())
        assert message["meeting_id"] == meeting_id
        assert message["text"] == "hello from fixture"
        assert message["speaker"]

    transcripts = client.get(f"/api/v1/transcripts/{meeting_id}")
    assert transcripts.status_code == 200
    rows = transcripts.json()
    assert len(rows) == 1
    assert rows[0]["text"] == "hello from fixture"

    summary = client.post(f"/api/v1/summary/{meeting_id}")
    assert summary.status_code == 200
    body = summary.json()
    assert "Mock summary" in body["summary_text"]
    assert isinstance(body["action_items"], list)
    assert body["action_items"][0]["task"]
