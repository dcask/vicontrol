from typing import List
from fastapi import WebSocket, WebSocketDisconnect

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        try:
            print('start broadcasting')
            for connection in self.active_connections:
                print('send')
                await connection.send_text(message)
        except WebSocketDisconnect:
            manager.disconnect(websocket)
            print(f"Client left the chat")

        


manager = ConnectionManager()


