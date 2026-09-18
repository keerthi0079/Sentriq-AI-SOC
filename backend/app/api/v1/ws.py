import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.websocket_hub import websocket_hub, MessageType

logger = logging.getLogger("sentriq.ws_endpoint")

router = APIRouter(tags=["WebSocket Telemetry"])


@router.websocket("/ws/soc-telemetry")
async def soc_telemetry_websocket(websocket: WebSocket):
    """
    Real-time SOC telemetry streaming WebSocket endpoint.
    Broadcasts live events, threat detection alerts, incident correlations, and system KPIs.
    """
    await websocket_hub.connect(websocket)
    try:
        # Send initial handshake state
        await websocket.send_json({
            "type": MessageType.SYSTEM_MESSAGE.value,
            "data": {
                "message": "Connected to Sentriq Real-Time Telemetry Stream",
                "status": "ready",
                "active_clients": websocket_hub.connection_count,
            },
        })

        while True:
            # Listen for client heartbeat/messages
            message_text = await websocket.receive_text()
            try:
                msg_payload = json.loads(message_text)
            except Exception:
                msg_payload = {"action": message_text}

            action = msg_payload.get("action") or msg_payload.get("type", "").lower()

            if action in ("ping", "heartbeat"):
                await websocket.send_json({
                    "type": MessageType.PONG.value,
                    "data": {"status": "alive"},
                })
            elif action == "subscribe":
                filter_type = msg_payload.get("filter", "all")
                await websocket.send_json({
                    "type": MessageType.SYSTEM_MESSAGE.value,
                    "data": {"subscribed_filter": filter_type},
                })
            else:
                logger.debug(f"Received WebSocket client message: {msg_payload}")

    except WebSocketDisconnect:
        await websocket_hub.disconnect(websocket)
    except Exception as e:
        logger.warning(f"Unexpected WebSocket termination: {e}")
        await websocket_hub.disconnect(websocket)

