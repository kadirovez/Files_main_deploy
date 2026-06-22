
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.ws.connection_manager import manager
from backend.crud.chat.chat import chat_crud
from backend.crud.chat.messages import message_crud
from backend.models.auth.user import User
from backend.schemas.chat.messages import MessageOut
from backend.services.chat.helpers import build_chat_list_item


async def send_message(
        db: AsyncSession,
        current_user: User,
        chat_id: int,
        text: str,
) -> MessageOut:
    """ Sends message when enter is pressed """
    text = text.strip()
    if not text:
        raise HTTPException(status_code=400, detail='Message cannot be empty')

    if not await chat_crud.is_member(db=db, chat_id=chat_id, user_id=current_user.id):
        raise HTTPException(status_code=403, detail='Not a chat member')

    message = await message_crud.create_message(
        db=db,
        chat_id=chat_id,
        sender_id=current_user.id,
        text=text,
    )

    message_out = MessageOut(
        id=message.id,
        chat_id=message.chat_id,
        sender_id=message.sender_id,
        sender_username=current_user.username,
        text=message.text,
        created_at=message.created_at,
        is_read=message.is_read,
    )

    member_ids = await chat_crud.get_chat_member_ids(db=db, chat_id=chat_id)
    online_ids = manager.get_online_user_ids()
    chat = await chat_crud.get_with_details(db=db, chat_id=chat_id)

    message_payload = {
        'type': 'message',
        'message': message_out.model_dump(mode='json'),
    }

    for member_id in member_ids:
        await manager.send_to_user(member_id, message_payload)

        chat_item = build_chat_list_item(chat, member_id, online_ids)
        if chat_item:
            await manager.send_to_user(member_id, {
                'type': 'chat_updated',
                'chat': chat_item.model_dump(),
            })

    return message_out
