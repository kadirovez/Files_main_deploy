
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.crud.auth.user import user_crud
from backend.crud.chat.chat import chat_crud
from backend.crud.chat.messages import message_crud
from backend.models.auth.user import User
from backend.schemas.chat.messages import MessageOut


async def get_messages(
        db: AsyncSession,
        current_user: User,
        chat_id: int,
):
    """ Loads message history in chat """
    if not await chat_crud.is_member(db=db, chat_id=chat_id, user_id=current_user.id):
        raise HTTPException(
            status_code=403,
            detail='Not a chat member'
        )

    messages = await message_crud.get_chat_messages(db=db, chat_id=chat_id)
    usernames: dict[int, str] = {current_user.id: current_user.username}

    result: list[MessageOut] = []
    for message in messages:
        if message.sender_id not in usernames:
            sender = await user_crud.get(db=db, id=message.sender_id)
            usernames[sender.id] = sender.username

        result.append(MessageOut(
            id=message.id,
            chat_id=message.chat_id,
            sender_id=message.sender_id,
            sender_username=usernames[message.sender_id],
            text=message.text,
            created_at=message.created_at,
            is_read=message.is_read,
        ))

    return result
