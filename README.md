# Meeting API

[![ci](https://github.com/LifeAyush/meeting-api/actions/workflows/ci.yml/badge.svg)](https://github.com/LifeAyush/meeting-api/actions/workflows/ci.yml)

https://github.com/LifeAyush/meeting-api

FastAPI service that accepts meeting audio over a WebSocket, transcribes it with Whisper, matches speakers with Resemblyzer voice embeddings, stores transcripts in SQLite, and produces a summary with action items.

The server does **not** require a GPU. Demo defaults use Whisper `tiny` and `SUMMARY_MODE=mock` (no OpenAI key).

## What it does

- **REST** — create/get meetings, list transcripts, create/get summaries (`/api/v1/...`)
- **Stream audio** — `ws://localhost:8000/ws/meetings/{meeting_id}` accepts raw WAV bytes
- **Whisper transcription** — model from `WHISPER_MODEL` (default `tiny`; use `base` for higher quality)
- **Speaker matching** — Resemblyzer embeddings compared per meeting (not full pyannote diarization)
- **Summary** — mock template by default, or OpenAI JSON summary + action items when `SUMMARY_MODE=openai`

## Requirements

- Python 3.11+
- [ffmpeg](https://ffmpeg.org/) on `PATH` (Whisper)
- Optional: `OPENAI_API_KEY` when using OpenAI summaries

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python scripts/gen_fixture_wav.py
uvicorn app.main:app --reload
```

In another terminal:

```bash
python scripts/demo.py
```

That creates a meeting, uploads `fixtures/demo.wav`, prints transcripts, and returns a mock summary with action items.

### Docker

```bash
python scripts/gen_fixture_wav.py
docker compose up --build
python scripts/demo.py
```

Health: `GET /health` → `{"status":"ok"}`.

## Configuration

See [`.env.example`](.env.example).

| Variable | Default | Meaning |
| --- | --- | --- |
| `DATABASE_URL` | `sqlite:///./meetings.db` | SQLAlchemy URL |
| `WHISPER_MODEL` | `tiny` | Whisper checkpoint name |
| `SUMMARY_MODE` | `mock` | `mock` or `openai` |
| `OPENAI_API_KEY` | empty | Required for `SUMMARY_MODE=openai` |

## API sketch

```bash
# Create meeting
curl -s -X POST http://localhost:8000/api/v1/meetings/ \
  -H 'Content-Type: application/json' \
  -d '{"title":"Weekly sync"}'

# List transcripts
curl -s http://localhost:8000/api/v1/transcripts/<meeting_id>

# Summarize (POST) / fetch (GET)
curl -s -X POST http://localhost:8000/api/v1/summary/<meeting_id>
```

Summary JSON shape:

```json
{
  "id": 1,
  "meeting_id": "...",
  "summary_text": "...",
  "action_items": [{"owner": "spk1", "task": "...", "due_hint": "this week"}],
  "created_at": "..."
}
```

## Checks

```bash
pytest -q
```

CI runs pytest with Whisper/encoder boundaries mocked (no large model download required for the default suite). A manual WebSocket uploader remains at `testing/websocket_audio_chunk_upload_check.py` (originally contributed in the AniketMonty test commit).

## License

[MIT](LICENSE)
