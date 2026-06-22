
from datetime import datetime

from backend.models.auth.user import User
from backend.models.chats.chat import Chat
from backend.schemas.chat.chat import ChatListItem, LastMessagePreview, PeerInfo


def _get_peer(chat: Chat, current_user_id: int) -> User | None:
    for member in chat.members:
        if member.user_id != current_user_id:
            return member.user
    return None


def build_chat_list_item(
        chat: Chat,
        current_user_id: int,
        online_user_ids: set[int],
) -> ChatListItem | None:
    peer = _get_peer(chat, current_user_id)
    if peer is None:
        return None

    last_message = None
    if chat.messages:
        latest = max(chat.messages, key=lambda m: m.created_at)
        last_message = LastMessagePreview(
            id=latest.id,
            text=latest.text,
            sender_id=latest.sender_id,
            created_at=latest.created_at.isoformat(),
            is_mine=latest.sender_id == current_user_id,
        )

    created_at = chat.created_at
    if isinstance(created_at, datetime):
        created_at_str = created_at.isoformat()
    else:
        created_at_str = str(created_at)

    return ChatListItem(
        id=chat.id,
        peer=PeerInfo(
            id=peer.id,
            username=peer.username,
            first_name=peer.first_name,
            last_name=peer.last_name,
            is_online=peer.id in online_user_ids,
        ),
        last_message=last_message,
        created_at=created_at_str,
    )
