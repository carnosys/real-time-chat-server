from datetime import datetime

from pydantic import BaseModel

from app.schemas.base import ORMBaseModel


class MessageCreate(BaseModel):
    room_id: int
    sender_id: int
    content: str
    client_message_id: str


class MessageUpdate(BaseModel):
    content: str


class MessageRead(ORMBaseModel):
    id: int
    room_id: int
    sender_id: int
    content: str
    created_at: datetime
    is_read: bool
    client_message_id: str
