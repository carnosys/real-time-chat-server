from datetime import datetime

from pydantic import BaseModel

from app.schemas.base import ORMBaseModel


class UserCreate(BaseModel):
    display_name: str
    username: str
    password: str
    email: str


class UserLogin(BaseModel):
    username: str | None = None
    email: str | None = None
    password: str


class UserUpdate(BaseModel):
    display_name: str | None = None
    username: str | None = None
    password: str | None = None
    email: str | None = None


class UserRead(ORMBaseModel):
    id: int
    display_name: str
    username: str
    email: str
    created_at: datetime
