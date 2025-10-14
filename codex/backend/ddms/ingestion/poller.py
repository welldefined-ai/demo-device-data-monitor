from __future__ import annotations

import json
import logging
import struct
from contextlib import suppress
from datetime import UTC, datetime
from typing import Any, Literal

from pymodbus.client import ModbusSerialClient, ModbusTcpClient
from sqlalchemy.orm import Session, sessionmaker

from ddms.db.models import Device, DeviceStatus
from ddms.db.repositories.devices import update_device
from ddms.db.repositories.readings import create_reading

logger = logging.getLogger(__name__)

INT16_SIGN_BIT = 0x8000
MIN_32BIT_WORDS = 2


ByteOrder = Literal["big", "little"]


def _parse_modbus_number(
    registers: list[int], data_type: str = "uint16", byteorder: ByteOrder = "big"
) -> float:
    """Parse registers into a numeric value.

    Supports common types: uint16, int16, uint32, int32, float32.
    """
    if not registers:
        raise ValueError("no registers")

    def _to_bytes(words: list[int]) -> bytes:
        b = bytearray()
        for w in words:
            b.extend(w.to_bytes(2, byteorder=byteorder, signed=False))
        return bytes(b)

    dt = data_type.lower()
    if dt in {"uint16", "int16"}:
        val = int(registers[0] & 0xFFFF)
        if dt == "int16" and val >= INT16_SIGN_BIT:
            val = val - 0x10000
        return float(val)
    if dt in {"uint32", "int32", "float32"}:
        if len(registers) < MIN_32BIT_WORDS:
            raise ValueError("insufficient register count for 32-bit value")
        data = _to_bytes(registers[:2])
        if dt == "float32":
            return float(struct.unpack(">f" if byteorder == "big" else "<f", data)[0])
        # integer 32-bit
        u = int.from_bytes(data, byteorder=byteorder, signed=(dt == "int32"))
        return float(u)
    raise ValueError(f"unsupported data_type: {data_type}")


def _read_modbus(cfg: dict[str, Any]) -> float:
    """Read a value from Modbus according to configuration.

    Expected cfg keys:
      - type: "tcp" | "rtu"
      - host/port (for tcp) or port/baudrate (for rtu)
      - unit_id: int (slave id), default 1
      - register: int (address)
      - count: int (default depends on data_type)
      - data_type: "uint16" | "int16" | "uint32" | "int32" | "float32"
      - byteorder: "big" | "little" (default big)
    """
    typ = str(cfg.get("type", "tcp")).lower()
    data_type = str(cfg.get("data_type", "uint16")).lower()
    byteorder_raw = str(cfg.get("byteorder", "big")).lower()
    unit = int(cfg.get("unit_id", 1))
    register = int(cfg.get("register", 0))
    count = int(cfg.get("count", 2 if data_type in {"uint32", "int32", "float32"} else 1))

    if typ == "tcp":
        host = cfg.get("host", "127.0.0.1")
        port = int(cfg.get("port", 502))
        client: Any = ModbusTcpClient(host=host, port=port, timeout=2)
    elif typ == "rtu":
        serial_port = cfg.get("port", "/dev/ttyUSB0")
        baudrate = int(cfg.get("baudrate", 9600))
        client = ModbusSerialClient(port=serial_port, baudrate=baudrate, timeout=2)
    else:
        raise ValueError("unsupported modbus type")

    if not client.connect():
        raise ConnectionError("unable to connect")
    try:
        # Using holding registers as common case; could be extended with cfg
        rr = client.read_holding_registers(address=register, count=count, unit=unit)
        if rr.isError():
            raise ConnectionError(str(rr))
        regs: list[int] = list(rr.registers)
        order: ByteOrder = "little" if byteorder_raw == "little" else "big"
        return _parse_modbus_number(regs, data_type=data_type, byteorder=order)
    finally:
        with suppress(Exception):  # pragma: no cover - defensive
            client.close()


def poll_device(session_factory: sessionmaker[Session], device_id: int) -> None:
    """Poll a single device and persist a reading.

    Safe to call from a background scheduler. Uses a short-lived DB session.
    """
    session = session_factory()
    try:
        d = session.get(Device, device_id)
        if not d:
            return
        cfg = json.loads(d.modbus_config or "{}")
        try:
            value = _read_modbus(cfg)
            ts = datetime.now(UTC)
            create_reading(session, device_id=d.id, timestamp=ts, value=float(value))
            # mark device online and update last_reading_at
            update_device(session, d, status=DeviceStatus.ONLINE)
            d.last_reading_at = ts
            session.add(d)
            session.commit()
        except Exception as err:  # pragma: no cover - network dependent
            logger.debug("Polling device %s failed: %s", d.id, err)
            # Conservative: mark offline on connection issues, else error
            status = DeviceStatus.ERROR
            if isinstance(err, ConnectionError):
                status = DeviceStatus.OFFLINE
            update_device(session, d, status=status)
    finally:
        session.close()
