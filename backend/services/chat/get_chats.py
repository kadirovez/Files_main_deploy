
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.ws.connection_manager import manager
from backend.crud.chat.chat import chat_crud
from backend.models.auth.user import User
from backend.services.chat.helpers import build_chat_list_item


async def get_chats(
        db: AsyncSession,
        current_user: User,
):
    """ Service for getting all existing chats """
    chats = await chat_crud.get_user_chats(db=db, user_id=current_user.id)
    online_ids = manager.get_online_user_ids()

    items = []
    for chat in chats:
        item = build_chat_list_item(chat, current_user.id, online_ids)
        if item:
            items.append(item)

    items.sort(
        key=lambda c: c.last_message.created_at if c.last_message else c.created_at,
        reverse=True,
    )
    return items

