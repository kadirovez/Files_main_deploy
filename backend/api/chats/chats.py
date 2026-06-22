
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.deps.database import get_db
from backend.deps.user import get_current_user
from backend.models.auth.user import User
from backend.schemas.chat.chat import ChatListItem, CreateChatRequest
from backend.schemas.chat.messages import MessageOut, SendMessageRequest
from backend.services.chat import chat_service

router = APIRouter(prefix='/chats', tags=['chats'])


@router.get('/', response_model=list[ChatListItem])
async def list_chats(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
):
    """ Gets all existing chats where user is member, for the dashboard """
    return await chat_service.get_chats(db=db, current_user=current_user)


@router.post('/', response_model=ChatListItem)
async def create_chat(
        body: CreateChatRequest,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
):
    """ Creates cheat, or returns existing one """
    return await chat_service.create_chat(
        db=db,
        current_user=current_user,
        username=body.username,
    )


@router.get('/{chat_id}/messages', response_model=list[MessageOut])
async def list_messages(
        chat_id: int,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
):
    """ Loads messages """
    return await chat_service.get_messages(
        db=db,
        current_user=current_user,
        chat_id=chat_id,
    )


@router.post('/{chat_id}/messages', response_model=MessageOut)
async def send_message(
        chat_id: int,
        body: SendMessageRequest,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
):
    """ Sends message """
    return await chat_service.send_message(
        db=db,
        current_user=current_user,
        chat_id=chat_id,
        text=body.text,
    )
