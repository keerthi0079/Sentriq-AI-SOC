import asyncio
import json
import logging
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger("sentriq.websocket")


class MessageType(str, Enum):
    EVENT_INGESTED = "EVENT_INGESTED"
    DETECTION_ALERT = "DETECTION_ALERT"
    INCIDENT_CREATED = "INCIDENT_CREATED"
    INCIDENT_UPDATED = "INCIDENT_UPDATED"
    METRICS_UPDATE = "METRICS_UPDATE"
    STREAM_STATUS = "STREAM_STATUS"
    PONG = "PONG"
    SYSTEM_MESSAGE = "SYSTEM_MESSAGE"


class WebSocketHub:
    """Thread-safe WebSocket Connection Hub managing active client connections and broadcasting telemetry."""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> None:
        """Accepts a WebSocket connection and registers it in the active set."""
        await websocket.accept()
        async with self._lock:
            self.active_connections.add(websocket)
        logger.info(f"WebSocket client connected. Total active: {len(self.active_connections)}")

    async def disconnect(self, websocket: WebSocket) -> None:
        """Removes a WebSocket connection from the active set."""
        async with self._lock:
            self.active_connections.discard(websocket)
        logger.info(f"WebSocket client disconnected. Total active: {len(self.active_connections)}")

    async def send_personal(self, websocket: WebSocket, message: Dict[str, Any]) -> None:
        """Sends a JSON-serialized message to a single specific connection."""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.warning(f"Failed to send personal WebSocket message: {e}")
            await self.disconnect(websocket)

    async def broadcast(self, message: Dict[str, Any]) -> None:
        """Broadcasts a typed JSON telemetry message to all currently connected clients."""
        async with self._lock:
            connections = list(self.active_connections)

        if not connections:
            return

        dead_connections: List[WebSocket] = []
        for connection in connections:
            try:
                await connection.send_json(message)
            except (WebSocketDisconnect, RuntimeError, Exception) as e:
                logger.debug(f"Dead connection detected during broadcast: {e}")
                dead_connections.append(connection)

        if dead_connections:
            async with self._lock:
                for dead in dead_connections:
                    self.active_connections.discard(dead)

    async def broadcast_typed(self, message_type: MessageType, data: Any) -> None:
        """Helper to format and broadcast a typed message envelope."""
        envelope = {
            "type": message_type.value,
            "data": data,
        }
        await self.broadcast(envelope)

    @property
    def connection_count(self) -> int:
        """Returns the number of active connected clients."""
        return len(self.active_connections)


# Global singleton instance
websocket_hub = WebSocketHub()

