from fastapi import WebSocket

from app.websocket_handler import handle_ws

async def websocket_endpoint(websocket: WebSocket, meeting_id: str):
    await handle_ws(websocket, meeting_id)
