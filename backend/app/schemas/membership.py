from datetime import datetime

from pydantic import BaseModel

from app.schemas.base import ORMBaseModel


class MembershipCreate(BaseModel):
    room_id: int
    user_id: int


class MembershipRead(ORMBaseModel):
    room_id: int
    user_id: int
    joined_at: datetime
