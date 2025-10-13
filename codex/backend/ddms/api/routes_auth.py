from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from ddms.api.deps import get_current_user
from ddms.core.security import create_jwt, hash_password, set_auth_cookie, clear_auth_cookie, verify_password
from ddms.db.models import User
from ddms.db.repositories.users import get_by_username
from ddms.db.session import get_session
from ddms.schemas.users import LoginRequest, LoginResponse, UserOut


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, response: Response, session: Session = Depends(get_session)) -> LoginResponse:
    user = get_by_username(session, payload.username)
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_jwt({"sub": user.id, "role": user.role.value})
    response.set_cookie(**set_auth_cookie(token))
    return LoginResponse(user=UserOut.model_validate(user))


@router.post("/logout")
def logout(response: Response) -> dict[str, bool]:
    response.set_cookie(**clear_auth_cookie())
    return {"ok": True}


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)) -> UserOut:
    return UserOut.model_validate(current_user)
