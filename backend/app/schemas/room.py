from datetime import datetime

from pydantic import BaseModel

from app.schemas.base import ORMBaseModel


class RoomCreate(BaseModel):
    name: str
    created_by: int
    is_private: bool = False


class RoomUpdate(BaseModel):
    name: str | None = None
    is_private: bool | None = None


class RoomRead(ORMBaseModel):
    id: int
    name: str
    created_by: int
    created_at: datetime
    is_private: bool
