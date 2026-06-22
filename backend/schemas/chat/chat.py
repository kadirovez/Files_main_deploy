
from pydantic import BaseModel, ConfigDict


class ChatCreate(BaseModel):
    pass


class ChatUpdate(BaseModel):
    pass


class PeerInfo(BaseModel):
    id: int
    username: str
    first_name: str
    last_name: str
    is_online: bool

    model_config = ConfigDict(from_attributes=True)


class LastMessagePreview(BaseModel):
    id: int
    text: str
    sender_id: int
    created_at: str
    is_mine: bool

    model_config = ConfigDict(from_attributes=True)


class ChatListItem(BaseModel):
    id: int
    peer: PeerInfo
    last_message: LastMessagePreview | None = None
    created_at: str


class CreateChatRequest(BaseModel):
    username: str
