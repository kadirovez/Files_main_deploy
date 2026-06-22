
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.ws.connection_manager import manager
from backend.crud.auth.user import user_crud
from backend.crud.chat.chat import chat_crud
from backend.models.auth.user import User
from backend.services.chat.helpers import build_chat_list_item


async def create_chat(
        db: AsyncSession,
        current_user: User,
        username: str,
):
    """ Obviously it creates chat """
    username = username.strip()
    if not username:
        raise HTTPException(
            status_code=400,
            detail='Username is required'
        )

    if username == current_user.username:
        raise HTTPException(
            status_code=400,
            detail='Cannot chat with yourself'
        )

    peer = await user_crud.get_by_username(db=db, username=username)
    if peer is None:
        raise HTTPException(
            status_code=404,
            detail='User not found'
        )

    chat, created = await chat_crud.get_or_create_dialog(
        db=db,
        user_a=current_user.id,
        user_b=peer.id,
    )

    online_ids = manager.get_online_user_ids()
    chat_item = build_chat_list_item(chat, current_user.id, online_ids)

    if created:
        """ If chat was created for the first time, a companion will be notified """
        peer_item = build_chat_list_item(chat, peer.id, online_ids)
        if peer_item:
            await manager.send_to_user(peer.id, {
                'type': 'new_chat',
                'chat': peer_item.model_dump(),
            })

    return chat_item

