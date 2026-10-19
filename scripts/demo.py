#!/usr/bin/env python3
"""One-shot demo: create meeting → upload fixture WAV → list transcripts → summarize."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

import httpx
import websockets

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FIXTURE = ROOT / "fixtures" / "demo.wav"


async def upload_wav(ws_url: str, wav_path: Path) -> dict | None:
    async with websockets.connect(ws_url) as websocket:
        await websocket.send(wav_path.read_bytes())
        try:
            message = await asyncio.wait_for(websocket.recv(), timeout=120)
            return json.loads(message)
        except TimeoutError:
            print("Timed out waiting for transcript", file=sys.stderr)
            return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Meeting API end-to-end demo")
    parser.add_argument("--base", default="http://127.0.0.1:8000", help="API base URL")
    parser.add_argument("--wav", type=Path, default=DEFAULT_FIXTURE, help="WAV file to upload")
    parser.add_argument("--title", default="Demo meeting")
    args = parser.parse_args()

    if not args.wav.exists():
        print(f"Missing fixture WAV: {args.wav}", file=sys.stderr)
        print("Run: python scripts/gen_fixture_wav.py", file=sys.stderr)
        return 1

    base = args.base.rstrip("/")
    with httpx.Client(base_url=base, timeout=120.0) as client:
        health = client.get("/health")
        health.raise_for_status()
        meeting = client.post("/api/v1/meetings/", json={"title": args.title})
        meeting.raise_for_status()
        meeting_id = meeting.json()["id"]
        print(f"meeting_id={meeting_id}")

        ws_url = base.replace("http://", "ws://").replace("https://", "wss://")
        ws_url = f"{ws_url}/ws/meetings/{meeting_id}"
        payload = asyncio.run(upload_wav(ws_url, args.wav))
        print("ws_payload=", json.dumps(payload, indent=2))

        transcripts = client.get(f"/api/v1/transcripts/{meeting_id}")
        transcripts.raise_for_status()
        print("transcripts=", json.dumps(transcripts.json(), indent=2, default=str))

        summary = client.post(f"/api/v1/summary/{meeting_id}")
        summary.raise_for_status()
        print("summary=", json.dumps(summary.json(), indent=2, default=str))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
