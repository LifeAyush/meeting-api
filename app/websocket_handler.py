from typing import Dict, List
from fastapi import WebSocket, WebSocketDisconnect


class ConnectionManager:
    """Manages active WebSocket connections for meetings."""

    def __init__(self) -> None:
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, meeting_id: str) -> None:
        """Accept and register a new WebSocket connection for a meeting."""
        await websocket.accept()
        self.active_connections.setdefault(meeting_id, []).append(websocket)

    def disconnect(self, websocket: WebSocket, meeting_id: str) -> None:
        """Remove a WebSocket connection from a meeting."""
        self.active_connections[meeting_id].remove(websocket)

    async def broadcast(self, message: str, meeting_id: str) -> None:
        """Send a message to all WebSocket connections for a meeting."""
        for connection in self.active_connections.get(meeting_id, []):
            await connection.send_text(message)


manager = ConnectionManager()


async def handle_ws(websocket: WebSocket, meeting_id: str) -> None:
    """Handle a WebSocket connection for a meeting, broadcasting received messages."""
    await manager.connect(websocket, meeting_id)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Message: {data}", meeting_id)
    except WebSocketDisconnect:
        manager.disconnect(websocket, meeting_id)
