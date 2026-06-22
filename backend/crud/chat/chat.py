
from fastapi import HTTPException
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.crud.base import CRUDBase
from backend.models.chats.chat import Chat
from backend.models.chats.chat_member import ChatMember
from backend.schemas.chat.chat import ChatCreate, ChatUpdate


class CRUDChat(CRUDBase[Chat, ChatCreate, ChatUpdate]):

    async def get_user_chats(
            self,
            db: AsyncSession,
            user_id: int,
    ) -> list[Chat]:
        """ Gets all chats for user """
        query = (
            select(Chat)
            .join(ChatMember, ChatMember.chat_id == Chat.id)
            .where(ChatMember.user_id == user_id)
            .options(
                selectinload(Chat.members).selectinload(ChatMember.user),
                selectinload(Chat.messages),
            )
        )
        result = await db.execute(query)
        return list(result.scalars().unique().all())


    async def get_or_create_dialog(
            self,
            db: AsyncSession,
            user_a: int,
            user_b: int,
    ) -> tuple[Chat, bool]:
        """ Creates s new chat or return existing one """
        query = (
            select(Chat)
            .join(ChatMember, ChatMember.chat_id == Chat.id)
            .where(ChatMember.user_id == user_a)
            .where(
                Chat.id.in_(
                    select(ChatMember.chat_id).where(ChatMember.user_id == user_b)
                )
            )
            .options(
                selectinload(Chat.members).selectinload(ChatMember.user),
                selectinload(Chat.messages),
            )
        )
        result = await db.execute(query)
        chat = result.scalar_one_or_none()

        if chat:
            return chat, False

        chat = Chat()
        db.add(chat)
        await db.flush()

        db.add(ChatMember(chat_id=chat.id, user_id=user_a))
        db.add(ChatMember(chat_id=chat.id, user_id=user_b))
        await db.commit()

        result = await db.execute(
            select(Chat)
            .where(Chat.id == chat.id)
            .options(
                selectinload(Chat.members).selectinload(ChatMember.user),
                selectinload(Chat.messages),
            )
        )
        return result.scalar_one(), True


    async def get_chat_member_ids(
            self,
            db: AsyncSession,
            chat_id: int,
    ) -> list[int] :
        """ Gets gets ids of all chat members """
        query = select(ChatMember.user_id).where(ChatMember.chat_id == chat_id)
        result = await db.execute(query)
        return list(result.scalars().all())


    # async def is_member(
    #         self,
    #         db: AsyncSession,
    #         chat_id: int,
    #         user_id: int,
    # ) -> bool:
    #     """ Checks if user is member of chat """
    #     query = select(ChatMember).where(
    #         and_(ChatMember.chat_id == chat_id, ChatMember.user_id == user_id)
    #     )
    #     result = await db.execute(query)
    #     return result.scalar_one_or_none() is None

    async def is_member(
            self,
            db: AsyncSession,
            chat_id: int,
            user_id: int,
    ) -> bool:
        """ Checks if user is member of chat """
        query = select(ChatMember).where(
            and_(ChatMember.chat_id == chat_id, ChatMember.user_id == user_id)
        )
        result = await db.execute(query)
        return result.scalar_one_or_none() is not None


    async def get_with_details(
            self,
            db: AsyncSession,
            chat_id: int,
    ) -> Chat:
        query = (
            select(Chat)
            .where(Chat.id == chat_id)
            .options(
                selectinload(Chat.members).selectinload(ChatMember.user),
                selectinload(Chat.messages),
            )
        )
        result = await db.execute(query)
        chat = result.scalar_one_or_none()
        if not chat:
            raise HTTPException(
                status_code=404,
                detail='Chat not found'
            )
        return chat


chat_crud = CRUDChat(Chat)
