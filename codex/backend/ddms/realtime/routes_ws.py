from __future__ import annotations

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from ddms.realtime.manager import manager

router = APIRouter(prefix="/ws", tags=["ws"])


@router.websocket("/live")
async def ws_live(websocket: WebSocket, device_id: int = Query(..., ge=1)) -> None:
    await manager.register(device_id, websocket)
    try:
        # Keep the connection open; we don't expect client messages other than pings
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.unregister(device_id, websocket)
    except Exception:
        manager.unregister(device_id, websocket)

