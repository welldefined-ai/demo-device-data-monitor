"""WebSocket endpoint for real-time device updates."""

import asyncio
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import select

from ddms.db.base import async_session_maker
from ddms.db.models import Device, Reading

logger = logging.getLogger(__name__)

router = APIRouter(tags=["websocket"])

# Track active WebSocket connections
active_connections: list[WebSocket] = []


@router.websocket("/ws/live")
async def websocket_live(websocket: WebSocket) -> None:
    """
    WebSocket endpoint for real-time device reading updates.

    Clients subscribe and receive device reading updates as they occur.
    """
    await websocket.accept()
    active_connections.append(websocket)
    logger.info(f"WebSocket client connected. Total connections: {len(active_connections)}")

    try:
        # Keep connection alive and send periodic updates
        while True:
            # Fetch latest readings for all devices
            async with async_session_maker() as session:
                # Get all devices with their latest reading
                stmt = select(Device)
                result = await session.execute(stmt)
                devices = result.scalars().all()

                device_data = []
                for device in devices:
                    # Get latest reading for this device
                    reading_stmt = (
                        select(Reading)
                        .where(Reading.device_id == device.id)
                        .order_by(Reading.timestamp.desc())
                        .limit(1)
                    )
                    reading_result = await session.execute(reading_stmt)
                    latest_reading = reading_result.scalar_one_or_none()

                    if latest_reading:
                        device_data.append(
                            {
                                "device_id": device.id,
                                "device_name": device.name,
                                "unit": device.unit,
                                "value": latest_reading.value,
                                "timestamp": latest_reading.timestamp.isoformat(),
                                "status": device.status,
                                "thresholds": device.thresholds,
                            }
                        )

                # Send updates to client
                if device_data:
                    await websocket.send_json({"type": "readings", "data": device_data})

            # Wait before next update (2 seconds)
            await asyncio.sleep(2)

    except WebSocketDisconnect:
        active_connections.remove(websocket)
        logger.info(f"WebSocket client disconnected. Total connections: {len(active_connections)}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if websocket in active_connections:
            active_connections.remove(websocket)
