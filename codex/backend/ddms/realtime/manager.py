from __future__ import annotations

import asyncio
import json
import logging
from collections import defaultdict
from typing import Any

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WebSocketManager:
    """In-process pub/sub for device reading updates.

    - Subscribers connect via WebSocket and register to a specific device_id.
    - The poller enqueues messages from a background thread.
    - An asyncio task broadcasts enqueued messages to subscribers.
    """

    def __init__(self) -> None:
        self._connections: dict[int, set[WebSocket]] = defaultdict(set)
        self._queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
        self._loop: asyncio.AbstractEventLoop | None = None
        self._task: asyncio.Task[None] | None = None

    def attach_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop

    def start(self) -> None:
        if self._task is not None:
            return
        loop = asyncio.get_event_loop()
        self.attach_loop(loop)
        self._task = loop.create_task(self._run())

    async def _run(self) -> None:
        while True:
            msg = await self._queue.get()
            device_id = int(msg.get("device_id", 0))
            if not device_id:
                continue
            data = json.dumps(msg, separators=(",", ":"))
            conns = list(self._connections.get(device_id, set()))
            if not conns:
                continue
            to_drop: list[WebSocket] = []
            for ws in conns:
                try:
                    await ws.send_text(data)
                except Exception:  # pragma: no cover - network
                    to_drop.append(ws)
            for ws in to_drop:
                self._connections[device_id].discard(ws)

    async def register(self, device_id: int, ws: WebSocket) -> None:
        await ws.accept()
        self._connections[device_id].add(ws)
        # Send a hello/ack message
        await ws.send_text(json.dumps({"type": "subscribed", "device_id": device_id}))

    def unregister(self, device_id: int, ws: WebSocket) -> None:
        self._connections[device_id].discard(ws)

    def publish(self, *, device_id: int, payload: dict[str, Any]) -> None:
        """Thread-safe enqueue for broadcasting to all subscribers of a device."""
        msg = {"device_id": device_id, **payload}
        if self._loop is None:
            # No loop attached yet; drop silently
            return
        try:
            self._loop.call_soon_threadsafe(self._queue.put_nowait, msg)
        except Exception:  # pragma: no cover - best-effort
            logger.debug("WS publish drop: %s", msg)


# Global manager instance used across the app
manager = WebSocketManager()
