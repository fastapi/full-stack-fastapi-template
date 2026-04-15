import asyncio
from typing import Any
from uuid import UUID

from fastapi import WebSocket

from app.models import NotificationPublic


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: dict[UUID, list[WebSocket]] = {}
        self._lock: asyncio.Lock = asyncio.Lock()

    async def connect(self, user_id: UUID, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            if user_id not in self.active_connections:
                self.active_connections[user_id] = []
            self.active_connections[user_id].append(websocket)

    def disconnect(self, user_id: UUID, websocket: WebSocket) -> None:
        if user_id in self.active_connections:
            try:
                self.active_connections[user_id].remove(websocket)
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
            except ValueError:
                pass

    async def send_personal_message(
        self, message: dict[str, Any] | str, user_id: UUID
    ) -> None:
        async with self._lock:
            if user_id in self.active_connections:
                for websocket in self.active_connections[user_id]:
                    try:
                        if isinstance(message, dict):
                            await websocket.send_json(message)
                        else:
                            await websocket.send_text(message)
                    except Exception:
                        self.disconnect(user_id, websocket)

    async def send_notification(
        self, notification: NotificationPublic, user_id: UUID
    ) -> None:
        message = {
            "type": "notification",
            "data": {
                "id": str(notification.id),
                "title": notification.title,
                "message": notification.message,
                "notification_type": notification.notification_type,
                "is_read": notification.is_read,
                "action_url": notification.action_url,
                "user_id": str(notification.user_id),
                "created_at": (
                    notification.created_at.isoformat()
                    if notification.created_at
                    else None
                ),
                "updated_at": (
                    notification.updated_at.isoformat()
                    if notification.updated_at
                    else None
                ),
            },
        }
        await self.send_personal_message(message, user_id)

    async def broadcast(self, message: dict[str, Any] | str) -> None:
        async with self._lock:
            for user_id, connections in list(self.active_connections.items()):
                for websocket in connections:
                    try:
                        if isinstance(message, dict):
                            await websocket.send_json(message)
                        else:
                            await websocket.send_text(message)
                    except Exception:
                        self.disconnect(user_id, websocket)


manager = ConnectionManager()
