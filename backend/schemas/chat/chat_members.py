
from pydantic import BaseModel


class ChatMemberCreate(BaseModel):
    chat_id: int
    user_id: int
