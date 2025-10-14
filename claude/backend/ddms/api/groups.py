"""Group management endpoints."""

import logging

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import func, select

from ddms.api.deps import CurrentUser, DbSession, ModifyUser
from ddms.db.models import Device, Group, GroupDevice
from ddms.schemas.device import DeviceResponse
from ddms.schemas.group import (
    DeviceAssignmentResponse,
    GroupCreate,
    GroupListResponse,
    GroupResponse,
    GroupUpdate,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/groups", tags=["groups"])


@router.get("", response_model=GroupListResponse)
async def list_groups(
    session: DbSession,
    current_user: CurrentUser,
) -> GroupListResponse:
    """
    List all groups.

    Args:
        session: Database session
        current_user: Current authenticated user

    Returns:
        List of all groups
    """
    # Query groups with device count
    stmt = (
        select(Group, func.count(GroupDevice.device_id).label("device_count"))
        .outerjoin(GroupDevice, Group.id == GroupDevice.group_id)
        .group_by(Group.id)
    )
    result = await session.execute(stmt)
    groups_with_counts = result.all()

    groups_response = []
    for group, device_count in groups_with_counts:
        group_dict = GroupResponse.model_validate(group).model_dump()
        group_dict["device_count"] = device_count
        groups_response.append(GroupResponse(**group_dict))

    logger.info(f"User {current_user.username} listed all groups ({len(groups_response)} total)")

    return GroupListResponse(
        groups=groups_response,
        total=len(groups_response),
    )


@router.get("/{group_id}/devices", response_model=list[DeviceResponse])
async def get_group_devices(
    group_id: int,
    session: DbSession,
    current_user: CurrentUser,
) -> list[DeviceResponse]:
    """
    Get all devices in a group.

    Args:
        group_id: Group ID
        session: Database session
        current_user: Current authenticated user

    Returns:
        List of devices in the group

    Raises:
        HTTPException: If group not found
    """
    # Verify group exists
    group_result = await session.execute(select(Group).where(Group.id == group_id))
    group = group_result.scalar_one_or_none()

    if group is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found",
        )

    # Get devices in group
    stmt = (
        select(Device)
        .join(GroupDevice, Device.id == GroupDevice.device_id)
        .where(GroupDevice.group_id == group_id)
    )
    result = await session.execute(stmt)
    devices = result.scalars().all()

    return [DeviceResponse.model_validate(device) for device in devices]


@router.post("", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
async def create_group(
    group_data: GroupCreate,
    session: DbSession,
    current_user: ModifyUser,
) -> GroupResponse:
    """
    Create a new group.

    Args:
        group_data: Group creation data
        session: Database session
        current_user: Current user (must have modify permissions)

    Returns:
        Created group information
    """
    new_group = Group(
        name=group_data.name,
        description=group_data.description,
    )

    session.add(new_group)
    await session.commit()
    await session.refresh(new_group)

    logger.info(
        f"User {current_user.username} created group: {new_group.name} (id: {new_group.id})"
    )

    return GroupResponse.model_validate(new_group)


@router.patch("/{group_id}", response_model=GroupResponse)
async def update_group(
    group_id: int,
    group_data: GroupUpdate,
    session: DbSession,
    current_user: ModifyUser,
) -> GroupResponse:
    """
    Update an existing group.

    Args:
        group_id: Group ID
        group_data: Update data
        session: Database session
        current_user: Current user (must have modify permissions)

    Returns:
        Updated group information

    Raises:
        HTTPException: If group not found
    """
    result = await session.execute(select(Group).where(Group.id == group_id))
    group = result.scalar_one_or_none()

    if group is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found",
        )

    # Apply updates
    if group_data.name is not None:
        group.name = group_data.name
    if group_data.description is not None:
        group.description = group_data.description

    await session.commit()
    await session.refresh(group)

    logger.info(f"User {current_user.username} updated group {group.name} (id: {group.id})")

    return GroupResponse.model_validate(group)


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(
    group_id: int,
    session: DbSession,
    current_user: ModifyUser,
) -> None:
    """
    Delete a group.

    Args:
        group_id: Group ID
        session: Database session
        current_user: Current user (must have modify permissions)

    Raises:
        HTTPException: If group not found
    """
    result = await session.execute(select(Group).where(Group.id == group_id))
    group = result.scalar_one_or_none()

    if group is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found",
        )

    await session.delete(group)
    await session.commit()

    logger.info(f"User {current_user.username} deleted group {group.name} (id: {group.id})")


@router.post("/{group_id}/devices/{device_id}", response_model=DeviceAssignmentResponse)
async def assign_device_to_group(
    group_id: int,
    device_id: int,
    session: DbSession,
    current_user: ModifyUser,
) -> DeviceAssignmentResponse:
    """
    Assign a device to a group.

    Args:
        group_id: Group ID
        device_id: Device ID
        session: Database session
        current_user: Current user (must have modify permissions)

    Returns:
        Assignment confirmation

    Raises:
        HTTPException: If group or device not found, or device already assigned
    """
    # Verify group exists
    group_result = await session.execute(select(Group).where(Group.id == group_id))
    group = group_result.scalar_one_or_none()
    if group is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found",
        )

    # Verify device exists
    device_result = await session.execute(select(Device).where(Device.id == device_id))
    device = device_result.scalar_one_or_none()
    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found",
        )

    # Check if device is already assigned to a group
    existing_result = await session.execute(
        select(GroupDevice).where(GroupDevice.device_id == device_id)
    )
    existing_assignment = existing_result.scalar_one_or_none()

    if existing_assignment is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Device is already assigned to group {existing_assignment.group_id}",
        )

    # Create assignment
    assignment = GroupDevice(group_id=group_id, device_id=device_id)
    session.add(assignment)
    await session.commit()

    logger.info(f"User {current_user.username} assigned device {device.name} to group {group.name}")

    return DeviceAssignmentResponse(
        message="Device assigned to group successfully",
        group_id=group_id,
        device_id=device_id,
    )


@router.delete("/{group_id}/devices/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_device_from_group(
    group_id: int,
    device_id: int,
    session: DbSession,
    current_user: ModifyUser,
) -> None:
    """
    Remove a device from a group.

    Args:
        group_id: Group ID
        device_id: Device ID
        session: Database session
        current_user: Current user (must have modify permissions)

    Raises:
        HTTPException: If assignment not found
    """
    result = await session.execute(
        select(GroupDevice).where(
            GroupDevice.group_id == group_id, GroupDevice.device_id == device_id
        )
    )
    assignment = result.scalar_one_or_none()

    if assignment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device assignment not found",
        )

    await session.delete(assignment)
    await session.commit()

    logger.info(f"User {current_user.username} removed device {device_id} from group {group_id}")
