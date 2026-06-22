
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MessageCreate(BaseModel):
    chat_id: int
    sender_id: int
    text: str


class MessageUpdate(BaseModel):
    is_read: bool | None = None
    text: str | None = None


class MessageOut(BaseModel):
    id: int
    chat_id: int
    sender_id: int
    sender_username: str | None = None
    text: str
    created_at: datetime
    is_read: bool

    model_config = ConfigDict(from_attributes=True)


class SendMessageRequest(BaseModel):
    text: str
