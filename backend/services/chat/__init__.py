
from backend.services.chat.create_chat import create_chat
from backend.services.chat.get_chats import get_chats
from backend.services.chat.get_messages import get_messages
from backend.services.chat.send_message import send_message


class ChatServices:
    get_chats = staticmethod(get_chats)
    create_chat = staticmethod(create_chat)
    get_messages = staticmethod(get_messages)
    send_message = staticmethod(send_message)


chat_service = ChatServices()
