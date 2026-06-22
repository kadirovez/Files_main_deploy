
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.crud.base import CRUDBase
from backend.models.chats.message import Message
from backend.schemas.chat.messages import MessageCreate, MessageUpdate


class CRUDMessage(CRUDBase[Message, MessageCreate, MessageUpdate]):

    async def get_chat_messages(
            self,
            db: AsyncSession,
            chat_id: int,
            limit: int = 200,
    ) -> list[Message]:
        """ Gets and sorts by date all messages in chat """
        query = (
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(Message.created_at.asc())
            .limit(limit)
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    async def create_message(
            self,
            db: AsyncSession,
            chat_id: int,
            sender_id: int,
            text: str,
    ) -> Message:
        """ Creates message """
        message = Message(
            chat_id=chat_id,
            sender_id=sender_id,
            text=text,
        )
        db.add(message)
        await db.commit()
        await db.refresh(message)
        return message


message_crud = CRUDMessage(Message)
