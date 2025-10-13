from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from ddms.api.deps import SessionDep, get_current_user, require_roles
from ddms.core.security import hash_password
from ddms.db.models import Role, User
from ddms.db.repositories.users import create_user, delete_user, get_by_username, list_users, update_user
from ddms.db.session import get_session
from ddms.schemas.users import UserCreate, UserOut, UserUpdate


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[UserOut], dependencies=[Depends(require_roles(Role.ADMIN, Role.OWNER))])
def users_list(session: SessionDep) -> list[UserOut]:
    users = list_users(session)
    return [UserOut.model_validate(u) for u in users]


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles(Role.ADMIN, Role.OWNER))])
def users_create(payload: UserCreate, session: SessionDep) -> UserOut:
    if payload.role == Role.OWNER:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot create owner via API")
    if get_by_username(session, payload.username):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")
    user = create_user(session, username=payload.username, password_hash=hash_password(payload.password), role=payload.role)
    return UserOut.model_validate(user)


@router.patch("/{user_id}", response_model=UserOut)
def users_update(
    payload: UserUpdate,
    session: SessionDep,
    user_id: int = Path(..., ge=1),
    current_user: User = Depends(get_current_user),
) -> UserOut:
    target = session.get(User, user_id)
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Permission: owner/admin can update anyone; others can update self only
    if current_user.role not in (Role.OWNER, Role.ADMIN) and current_user.id != target.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    new_username = payload.username
    if new_username and new_username != target.username:
        if get_by_username(session, new_username):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")

    new_hash = hash_password(payload.password) if payload.password else None
    updated = update_user(session, target, username=new_username, password_hash=new_hash)
    return UserOut.model_validate(updated)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_roles(Role.ADMIN, Role.OWNER))])
def users_delete(user_id: int = Path(..., ge=1), session: SessionDep = Depends(get_session)) -> None:
    target = session.get(User, user_id)
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if target.role == Role.OWNER:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete owner account")
    delete_user(session, target)
    return None

