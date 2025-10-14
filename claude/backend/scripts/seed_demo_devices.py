#!/usr/bin/env python3
"""Seed demo devices for testing and demonstration."""

import asyncio
import sys

from sqlalchemy import select

from ddms.core.config import settings
from ddms.db.base import async_session_maker
from ddms.db.models import Device


async def seed_demo_devices():
    """Create 4 demo devices connected to the Modbus simulator."""

    devices_config = [
        {
            "name": "Tank Temperature Sensor",
            "description": "Main storage tank temperature monitoring",
            "unit": "°C",
            "sampling_interval": 2,
            "thresholds": {"warning": 28.0, "critical": 29.0},
            "modbus_config": {
                "type": "tcp",
                "host": "modbus-simulator",
                "port": 5020,
                "register": 40001,
                "data_type": "int16",
            },
        },
        {
            "name": "Tank Pressure Sensor",
            "description": "Hydraulic pressure in main tank",
            "unit": "bar",
            "sampling_interval": 2,
            "thresholds": {"warning": 85.0, "critical": 95.0},
            "modbus_config": {
                "type": "tcp",
                "host": "modbus-simulator",
                "port": 5020,
                "register": 40002,
                "data_type": "int16",
            },
        },
        {
            "name": "Pump Motor RPM",
            "description": "Circulation pump motor speed",
            "unit": "RPM",
            "sampling_interval": 2,
            "thresholds": {"warning": 2700.0, "critical": 2900.0},
            "modbus_config": {
                "type": "tcp",
                "host": "modbus-simulator",
                "port": 5020,
                "register": 40003,
                "data_type": "int16",
            },
        },
        {
            "name": "Environmental Humidity",
            "description": "Ambient humidity level",
            "unit": "%",
            "sampling_interval": 2,
            "thresholds": {"warning": 65.0, "critical": 70.0},
            "modbus_config": {
                "type": "tcp",
                "host": "modbus-simulator",
                "port": 5020,
                "register": 40004,
                "data_type": "int16",
            },
        },
    ]

    async with async_session_maker() as session:
        # Check if devices already exist
        result = await session.execute(select(Device))
        existing_devices = result.scalars().all()

        if existing_devices:
            print(f"Found {len(existing_devices)} existing devices. Clearing...")
            for device in existing_devices:
                await session.delete(device)
            await session.commit()
            print("Existing devices cleared.")

        # Create demo devices
        for device_cfg in devices_config:
            device = Device(
                name=device_cfg["name"],
                description=device_cfg["description"],
                unit=device_cfg["unit"],
                sampling_interval=device_cfg["sampling_interval"],
                thresholds=device_cfg["thresholds"],
                modbus_config=device_cfg["modbus_config"],
                status="offline",
            )
            session.add(device)
            print(f"Created: {device_cfg['name']} ({device_cfg['unit']})")

        await session.commit()
        print(f"\n✅ Successfully seeded {len(devices_config)} demo devices!")
        print("Restart backend to start polling: docker compose restart backend")


if __name__ == "__main__":
    print("Seeding demo devices...\n")
    try:
        asyncio.run(seed_demo_devices())
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
