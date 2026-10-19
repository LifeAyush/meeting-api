import asyncio
import sys

import websockets


async def send_audio_chunks(meeting_id: str, file_path: str) -> None:
    uri = f"ws://localhost:8000/ws/meetings/{meeting_id}"
    async with websockets.connect(uri) as websocket:
        print(f"Connected to {uri} with file: {file_path}")
        with open(file_path, "rb") as handle:
            await websocket.send(handle.read())
            print(f"Sent audio from {file_path}")
        try:
            while True:
                message = await websocket.recv()
                print(f"Received: {message}")
        except websockets.exceptions.ConnectionClosed:
            print("WebSocket closed")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python testing/websocket_audio_chunk_upload_check.py <meeting_id> <audio_file_path>")
        sys.exit(1)
    asyncio.run(send_audio_chunks(sys.argv[1], sys.argv[2]))
