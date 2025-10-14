"""Device polling service for reading Modbus data."""

import logging
from datetime import datetime

from pymodbus.exceptions import ModbusException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ddms.db.models import Device, Reading
from ddms.ingestion.modbus_client import ModbusClientWrapper

logger = logging.getLogger(__name__)


async def poll_device(device_id: int, session: AsyncSession) -> None:
    """
    Poll a device to read its current value via Modbus.

    This function:
    1. Fetches device configuration
    2. Connects to Modbus device
    3. Reads value from configured register
    4. Stores reading in database
    5. Updates device status and last_reading_at

    Args:
        device_id: ID of device to poll
        session: Database session

    """
    # Fetch device configuration
    result = await session.execute(select(Device).where(Device.id == device_id))
    device = result.scalar_one_or_none()

    if device is None:
        logger.warning(f"Device {device_id} not found, skipping poll")
        return

    logger.debug(f"Polling device {device.name} (id={device.id})")

    try:
        # Create Modbus client and read value
        with ModbusClientWrapper(device.modbus_config) as modbus:
            value = modbus.read_value()

            if value is None:
                raise ModbusException("Read returned None")  # type: ignore[no-untyped-call]

            # Store reading
            reading = Reading(
                device_id=device.id,
                timestamp=datetime.now(),
                value=value,
            )
            session.add(reading)

            # Update device status
            device.status = "online"
            device.last_reading_at = reading.timestamp

            await session.commit()

            logger.info(
                f"Device {device.name} (id={device.id}): "
                f"Read value {value} {device.unit} at {reading.timestamp}"
            )

    except ModbusException as e:
        # Modbus communication error
        device.status = "error"
        await session.commit()

        logger.error(f"Modbus error reading device {device.name} (id={device.id}): {e}")

    except Exception as e:
        # Unexpected error
        device.status = "error"
        await session.commit()

        logger.error(f"Unexpected error polling device {device.name} (id={device.id}): {e}")
