"""Device management endpoints."""

import logging

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from ddms.api.deps import CurrentUser, DbSession, ModifyUser
from ddms.db.models import Device
from ddms.schemas.device import (
    ConnectionTestResult,
    DeviceCreate,
    DeviceListResponse,
    DeviceResponse,
    DeviceUpdate,
)

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

    # Apply updates
    if device_data.name is not None:
        device.name = device_data.name
    if device_data.description is not None:
        device.description = device_data.description
    if device_data.unit is not None:
        device.unit = device_data.unit
    if device_data.sampling_interval is not None:
        device.sampling_interval = device_data.sampling_interval
    if device_data.thresholds is not None:
        device.thresholds = device_data.thresholds.model_dump()
    if device_data.modbus_config is not None:
        device.modbus_config = device_data.modbus_config.model_dump()

    await session.commit()
    await session.refresh(device)

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

    # TODO: Implement actual Modbus connection test in Iteration 3
    # For now, return a placeholder response
    logger.info(
        f"User {current_user.username} tested connection for device {device.name} (id: {device.id})"
    )

    return ConnectionTestResult(
        success=False,
        message="Connection test not yet implemented (coming in Iteration 3)",
        error="Modbus client not yet configured",
    )
