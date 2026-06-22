
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base


class Message(Base):
    __tablename__ = 'messages'

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    chat_id: Mapped[int] = mapped_column(
        ForeignKey('chat.id', ondelete='CASCADE'),
        index=True,
    )

    sender_id: Mapped[int] = mapped_column(
        ForeignKey('user.id', ondelete='CASCADE'),
        index=True,
    )

    text: Mapped[str] = mapped_column(
        String(4096),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    is_read: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default='false',
    )

    chat = relationship('Chat', back_populates='messages')
    sender = relationship('User', back_populates='messages')

