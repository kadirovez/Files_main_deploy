
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base


class ChatMember(Base):
    __tablename__ = 'chat_members'

    chat_id: Mapped[int] = mapped_column(
        ForeignKey('chat.id', ondelete='CASCADE'),
        primary_key=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey('user.id', ondelete='CASCADE'),
        primary_key=True,
    )

    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    chat = relationship('Chat', back_populates='members')
    user = relationship('User', back_populates='chat_members')
