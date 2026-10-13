# Meeting API

https://github.com/LifeAyush/meeting-api

Meeting API that streams audio, transcribes it with Whisper, identifies speakers, and writes a summary. Clients upload audio over a WebSocket; the service stores transcripts and can summarize a meeting.

## What it does

- **Stream audio.** Send raw audio bytes to `ws://localhost:8000/ws/meetings/{meeting_id}` (`app/api/v1/websocket.py`).
- **Whisper transcription.** Each upload is transcribed with the Whisper `base` model.
- **Speaker identification.** Resemblyzer voice embeddings match a chunk to a known speaker, or start a new speaker id.
- **Summary.** `app/services/summarizer.py` joins a meeting's transcripts and asks OpenAI (`gpt-4`) for a summary, then stores it.
- **REST API.** Meeting, transcript, and summary handlers live in `app/api/v1/routes/`. The app wires those routers and the WebSocket in `app/main.py`.

## Run

Dependencies are listed in `requirements.txt`. The process entrypoint is `app/main.py` (`app = create_app()`).

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The database defaults to SQLite at `sqlite:///./meetings.db`. Override it with `DATABASE_URL` (`app/db/session.py`). Summarization uses the OpenAI client, so set `OPENAI_API_KEY` before generating a summary.

`testing/websocket_audio_chunk_upload_check.py` uploads one audio file to the meeting WebSocket:

```bash
python testing/websocket_audio_chunk_upload_check.py <meeting_id> <audio_file>
```

Tests were added by AniketMonty.
