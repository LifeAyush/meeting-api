from typing import Dict, List
from fastapi import WebSocket, WebSocketDisconnect

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, meeting_id: str):
        await websocket.accept()
        self.active_connections.setdefault(meeting_id, []).append(websocket)

    def disconnect(self, websocket: WebSocket, meeting_id: str):
        self.active_connections[meeting_id].remove(websocket)

    async def broadcast(self, message: str, meeting_id: str):
        for connection in self.active_connections.get(meeting_id, []):
            await connection.send_text(message)

manager = ConnectionManager()

async def handle_ws(websocket: WebSocket, meeting_id: str):
    await manager.connect(websocket, meeting_id)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Message: {data}", meeting_id)
    except WebSocketDisconnect:
        manager.disconnect(websocket, meeting_id)
