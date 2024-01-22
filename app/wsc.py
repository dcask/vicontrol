from typing import List
from json import loads
from fastapi import WebSocket, WebSocketDisconnect
from validator import getTokenUser, _get_public_keys
class ViConnection:
    def __init__(self, websocket, dashboard, token, client_id):
        self.websocket = websocket
        self.dashboard = dashboard
        self.token     = token
        self.client_id = client_id
        self.username  = ''


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[ViConnection] = []
        self.keys = None
    def setHostKeys(self, baseurl):
        self.keys = _get_public_keys(baseurl)

    async def connect(self, websocket: WebSocket, client_id:str):
        await websocket.accept()
        data = loads(await websocket.receive_text())
        if 'dashboard' not in data or 'token' not in data:
           websocket.send_text("Unauthorized")
           return False
        ws = ViConnection( websocket, data['dashboard'] , data['token'], client_id)
        ws.username = getTokenUser(data['token'], self.keys)
        self.active_connections.append(ws)
        print(client_id, "connected")
        return True

    def disconnect(self, websocket:WebSocket):
        for c in self.active_connections:
            if c.websocket == websocket:
                self.active_connections.remove(c)

    async def send_personal_message(self, message: str, client_id:str):
        for connection in self.active_connections:
            if connection.client_id == client_id:
                 await connection.websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                 await connection.websocket.send_text(message)
            except WebSocketDisconnect:
                 manager.disconnect(connection.websocket)
                 print(f"a Client closed connection")

    def connection_list(self):
        return [ {'client_id':c.client_id, 'dashboard':c.dashboard, 'user':c.username,'ip':c.websocket.headers['x-forwarded-for']} for c in self.active_connections]

        


manager = ConnectionManager()


