
import json
from datetime import datetime

from fastapi import WebSocket


class ConnectionManager:

    """ Manager for WebSocket connections """
    def __init__(self):
        self.connections: dict[int, WebSocket] = {}
        self.usernames: dict[int, str] = {}

    async def connect(self, user_id: int, username: str, websocket: WebSocket):
        if user_id in self.connections:
            old_ws = self.connections[user_id]
            try:
                await old_ws.close()
            except Exception:
                pass

        await websocket.accept()
        self.connections[user_id] = websocket
        self.usernames[user_id] = username
        await self.broadcast_presence()


    def disconnect(self, user_id: int):
        self.connections.pop(user_id, None)
        self.usernames.pop(user_id, None)


    def get_online_user_ids(self) -> set[int]:
        return set(self.connections.keys())


    def is_online(self, user_id: int) -> bool:
        return user_id in self.connections


    async def send_to_user(self, user_id: int, data: dict):
        ws = self.connections.get(user_id)
        if ws:
            await ws.send_text(json.dumps(data, default=_json_default))

    # Sends info about users online/offline
    async def broadcast_presence(self):
        msg = {
            'type': 'presence',
            'online_user_ids': list(self.connections.keys()),
        }
        payload = json.dumps(msg)
        for ws in self.connections.values():
            await ws.send_text(payload)


def _json_default(value):
    if isinstance(value, datetime):
        return value.isoformat()
    raise TypeError(f'Object of type {type(value)} is not JSON serializable')


manager = ConnectionManager()

