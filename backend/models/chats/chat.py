
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base


class Chat(Base):
    __tablename__ = 'chat'

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    members = relationship('ChatMember', back_populates='chat', cascade='all, delete-orphan')
    messages = relationship('Message', back_populates='chat', cascade='all, delete-orphan')
