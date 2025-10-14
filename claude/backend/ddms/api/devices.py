"""Device management endpoints."""

import csv
import io
import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from pymodbus.exceptions import ModbusException
from sqlalchemy import select

from ddms.api.deps import CurrentUser, DbSession, ModifyUser
from ddms.core.config import settings
from ddms.db.models import Device, Reading
from ddms.ingestion.modbus_client import ModbusClientWrapper
from ddms.schemas.device import (
    ConnectionTestResult,
    DeviceCreate,
    DeviceListResponse,
    DeviceResponse,
    DeviceUpdate,
)
from ddms.schemas.reading import ReadingResponse, ReadingsListResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/devices", tags=["devices"])


@router.get("", response_model=DeviceListResponse)
async def list_devices(
    session: DbSession,
    current_user: CurrentUser,
) -> DeviceListResponse:
    """
    List all devices with their status.

    Args:
        session: Database session
        current_user: Current authenticated user

    Returns:
        List of all devices
    """
    result = await session.execute(select(Device))
    devices = result.scalars().all()

    logger.info(f"User {current_user.username} listed all devices ({len(devices)} total)")

    return DeviceListResponse(
        devices=[DeviceResponse.model_validate(device) for device in devices],
        total=len(devices),
    )


@router.post("", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
async def create_device(
    device_data: DeviceCreate,
    session: DbSession,
    current_user: ModifyUser,
) -> DeviceResponse:
    """
    Create a new device.

    Args:
        device_data: Device creation data
        session: Database session
        current_user: Current user (must have modify permissions)

    Returns:
        Created device information
    """
    # Convert Pydantic models to dict for JSON storage
    thresholds_dict = device_data.thresholds.model_dump() if device_data.thresholds else None
    modbus_config_dict = device_data.modbus_config.model_dump()

    new_device = Device(
        name=device_data.name,
        description=device_data.description,
        unit=device_data.unit,
        sampling_interval=device_data.sampling_interval,
        thresholds=thresholds_dict,
        modbus_config=modbus_config_dict,
        status="offline",
    )

    session.add(new_device)
    await session.commit()
    await session.refresh(new_device)

    # Add polling job for new device (skip in test environment)
    if settings.env != "test":
        from ddms.scheduler.manager import add_device_job

        add_device_job(new_device.id, new_device.sampling_interval)

    logger.info(
        f"User {current_user.username} created device: {new_device.name} (id: {new_device.id})"
    )

    return DeviceResponse.model_validate(new_device)


@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(
    device_id: int,
    session: DbSession,
    current_user: CurrentUser,
) -> DeviceResponse:
    """
    Get device details.

    Args:
        device_id: Device ID
        session: Database session
        current_user: Current authenticated user

    Returns:
        Device information

    Raises:
        HTTPException: If device not found
    """
    result = await session.execute(select(Device).where(Device.id == device_id))
    device = result.scalar_one_or_none()

    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found",
        )

    return DeviceResponse.model_validate(device)


@router.patch("/{device_id}", response_model=DeviceResponse)
async def update_device(
    device_id: int,
    device_data: DeviceUpdate,
    session: DbSession,
    current_user: ModifyUser,
) -> DeviceResponse:
    """
    Update an existing device.

    Args:
        device_id: Device ID
        device_data: Update data
        session: Database session
        current_user: Current user (must have modify permissions)

    Returns:
        Updated device information

    Raises:
        HTTPException: If device not found
    """
    result = await session.execute(select(Device).where(Device.id == device_id))
    device = result.scalar_one_or_none()

    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found",
        )

    # Track if sampling interval changed
    interval_changed = False

    # Apply updates
    if device_data.name is not None:
        device.name = device_data.name
    if device_data.description is not None:
        device.description = device_data.description
    if device_data.unit is not None:
        device.unit = device_data.unit
    if device_data.sampling_interval is not None:
        device.sampling_interval = device_data.sampling_interval
        interval_changed = True
    if device_data.thresholds is not None:
        device.thresholds = device_data.thresholds.model_dump()
    if device_data.modbus_config is not None:
        device.modbus_config = device_data.modbus_config.model_dump()

    await session.commit()
    await session.refresh(device)

    # Update polling job if sampling interval changed (skip in test environment)
    if interval_changed and settings.env != "test":
        from ddms.scheduler.manager import update_device_job

        update_device_job(device.id, device.sampling_interval)

    logger.info(f"User {current_user.username} updated device {device.name} (id: {device.id})")

    return DeviceResponse.model_validate(device)


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(
    device_id: int,
    session: DbSession,
    current_user: ModifyUser,
) -> None:
    """
    Delete a device (soft delete - retain historical data).

    Args:
        device_id: Device ID
        session: Database session
        current_user: Current user (must have modify permissions)

    Raises:
        HTTPException: If device not found
    """
    result = await session.execute(select(Device).where(Device.id == device_id))
    device = result.scalar_one_or_none()

    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found",
        )

    await session.delete(device)
    await session.commit()

    # Remove polling job for deleted device (skip in test environment)
    if settings.env != "test":
        from ddms.scheduler.manager import remove_device_job

        remove_device_job(device.id)

    logger.info(f"User {current_user.username} deleted device {device.name} (id: {device.id})")


@router.post("/{device_id}/test-connection", response_model=ConnectionTestResult)
async def test_device_connection(
    device_id: int,
    session: DbSession,
    current_user: CurrentUser,
) -> ConnectionTestResult:
    """
    Test Modbus connection to a device.

    Args:
        device_id: Device ID
        session: Database session
        current_user: Current authenticated user

    Returns:
        Connection test result

    Raises:
        HTTPException: If device not found
    """
    result = await session.execute(select(Device).where(Device.id == device_id))
    device = result.scalar_one_or_none()

    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found",
        )

    logger.info(
        f"User {current_user.username} testing connection "
        f"for device {device.name} (id: {device.id})"
    )

    # Test Modbus connection
    try:
        with ModbusClientWrapper(device.modbus_config) as modbus:
            value = modbus.read_value()

            if value is None:
                return ConnectionTestResult(
                    success=False,
                    message="Connection failed: No data received",
                    error="Modbus read returned None",
                )

            return ConnectionTestResult(
                success=True,
                message=f"Connection successful! Read value: {value} {device.unit}",
                error=None,
            )

    except ModbusException as e:
        return ConnectionTestResult(
            success=False,
            message="Modbus communication error",
            error=str(e),
        )

    except Exception as e:
        logger.error(f"Connection test error: {e}")
        return ConnectionTestResult(
            success=False,
            message="Connection test failed",
            error=str(e),
        )


@router.get("/{device_id}/readings/current", response_model=ReadingsListResponse)
async def get_current_readings(
    device_id: int,
    session: DbSession,
    current_user: CurrentUser,
    limit: int = 100,
) -> ReadingsListResponse:
    """
    Get recent readings for a device.

    Args:
        device_id: Device ID
        limit: Maximum number of readings to return (default: 100)
        session: Database session
        current_user: Current authenticated user

    Returns:
        List of recent readings ordered by timestamp (newest first)

    Raises:
        HTTPException: If device not found
    """
    # Verify device exists
    result = await session.execute(select(Device).where(Device.id == device_id))
    device = result.scalar_one_or_none()

    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found",
        )

    # Get recent readings
    stmt = (
        select(Reading)
        .where(Reading.device_id == device_id)
        .order_by(Reading.timestamp.desc())
        .limit(limit)
    )
    readings_result = await session.execute(stmt)
    readings = readings_result.scalars().all()

    return ReadingsListResponse(
        readings=[ReadingResponse.model_validate(r) for r in readings],
        total=len(readings),
    )


@router.get("/{device_id}/readings/history", response_model=ReadingsListResponse)
async def get_historical_readings(
    device_id: int,
    session: DbSession,
    current_user: CurrentUser,
    start: str | None = None,
    end: str | None = None,
) -> ReadingsListResponse:
    """
    Get historical readings for a device within a time range.

    Args:
        device_id: Device ID
        session: Database session
        current_user: Current authenticated user
        start: Start time (ISO8601 format), defaults to 24 hours ago
        end: End time (ISO8601 format), defaults to now

    Returns:
        List of readings within time range

    Raises:
        HTTPException: If device not found or invalid time format
    """
    # Verify device exists
    result = await session.execute(select(Device).where(Device.id == device_id))
    device = result.scalar_one_or_none()

    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found",
        )

    # Parse time range
    try:
        if end:
            end_time = datetime.fromisoformat(end.replace("Z", "+00:00"))
        else:
            end_time = datetime.now()

        if start:
            start_time = datetime.fromisoformat(start.replace("Z", "+00:00"))
        else:
            from datetime import timedelta

            start_time = end_time - timedelta(hours=24)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid time format: {e}",
        ) from None

    # Query readings within time range
    stmt = (
        select(Reading)
        .where(
            Reading.device_id == device_id,
            Reading.timestamp >= start_time,
            Reading.timestamp <= end_time,
        )
        .order_by(Reading.timestamp.asc())
    )
    readings_result = await session.execute(stmt)
    readings = readings_result.scalars().all()

    return ReadingsListResponse(
        readings=[ReadingResponse.model_validate(r) for r in readings],
        total=len(readings),
    )


@router.get("/{device_id}/readings/export")
async def export_readings_csv(
    device_id: int,
    session: DbSession,
    current_user: CurrentUser,
    start: str | None = None,
    end: str | None = None,
) -> StreamingResponse:
    """
    Export historical readings as CSV file.

    Args:
        device_id: Device ID
        session: Database session
        current_user: Current authenticated user
        start: Start time (ISO8601 format)
        end: End time (ISO8601 format)

    Returns:
        CSV file download

    Raises:
        HTTPException: If device not found
    """
    # Reuse history endpoint logic
    readings_response = await get_historical_readings(device_id, session, current_user, start, end)

    # Get device info for filename
    result = await session.execute(select(Device).where(Device.id == device_id))
    device = result.scalar_one()

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow(["Timestamp", "Value", "Unit"])

    # Write data rows
    for reading in readings_response.readings:
        writer.writerow(
            [
                reading.timestamp.isoformat(),
                reading.value,
                device.unit,
            ]
        )

    # Prepare response
    output.seek(0)
    filename = f"{device.name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
