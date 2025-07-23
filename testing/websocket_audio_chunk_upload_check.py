import asyncio
import websockets
import sys

async def send_audio_chunks(meeting_id, file_path):
    uri = f"ws://localhost:8000/ws/meetings/{meeting_id}"
    async with websockets.connect(uri) as websocket:
        print(f"Connected to {uri} with file: {file_path}")

        # Send audio chunk
        with open(file_path, "rb") as f:
            audio_bytes = f.read()
            await websocket.send(audio_bytes)
            print(f"Sent audio from {file_path}")

        # Receive transcript from server
        try:
            while True:
                message = await websocket.recv()
                print(f"[{file_path} Received]:", message)
        except websockets.exceptions.ConnectionClosed:
            print("WebSocket closed")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python test_client.py <meeting_id> <audio_file_path>")
        sys.exit(1)

    meeting_id = sys.argv[1]
    file_path = sys.argv[2]

    asyncio.run(send_audio_chunks(meeting_id, file_path))
