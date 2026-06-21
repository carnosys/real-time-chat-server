# app/websockets/manager.py

from fastapi import WebSocket


class WebSocketManager:
    def __init__(self):
        self.active_connections: dict[int, WebSocket] = {}
        self.rooms: dict[int, set[int]] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        self.active_connections.pop(user_id, None)

        for room_users in self.rooms.values():
            room_users.discard(user_id)

    def join_room(self, user_id: int, room_id: int):
        if room_id not in self.rooms:
            self.rooms[room_id] = set()

        self.rooms[room_id].add(user_id)

    def leave_room(self, user_id: int, room_id: int):
        if room_id in self.rooms:
            self.rooms[room_id].discard(user_id)

            if not self.rooms[room_id]:
                del self.rooms[room_id]

    async def send_to_user(self, recipient_id: int, payload: dict):
        websocket = self.active_connections.get(recipient_id)

        if websocket:
            await websocket.send_json(payload)

    async def send_to_room(
        self,
        room_id: int,
        payload: dict,
        exclude_user_id: int | None = None,
    ):
        user_ids = self.rooms.get(room_id, set())

        for user_id in list(user_ids):
            if user_id == exclude_user_id:
                continue

            websocket = self.active_connections.get(user_id)

            if websocket:
                await websocket.send_json(payload)

    async def broadcast(self, payload: dict):
        for websocket in list(self.active_connections.values()):
            await websocket.send_json(payload)

    def is_user_online(self, user_id: int) -> bool:
        return user_id in self.active_connections

    def is_online(self, user_id: int) -> bool:
        return self.is_user_online(user_id)


manager = WebSocketManager()
