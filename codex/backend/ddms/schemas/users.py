from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from ddms.db.models import Role


class UserOut(BaseModel):
    id: int
    username: str
    role: Role
    language_preference: str = Field(default="en")
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserCreate(BaseModel):
    username: str
    password: str
    role: Role


class UserUpdate(BaseModel):
    username: str | None = None
    password: str | None = None


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    user: UserOut
