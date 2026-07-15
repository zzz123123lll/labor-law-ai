"""对话消息模型。"""
from sqlalchemy import ForeignKey, Integer, JSON, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid

from app.models.base import Base, TimestampMixin


class CaseMessage(Base, TimestampMixin):
    __tablename__ = "case_messages"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("cases.id"), index=True)
    role: Mapped[str] = mapped_column(String(16))  # user | assistant | system
    content: Mapped[str] = mapped_column(Text)
    msg_type: Mapped[str] = mapped_column(String(16), default="text")
    metadata_: Mapped[dict] = mapped_column("metadata", JSON, default=dict)
    token_used: Mapped[int | None] = mapped_column(Integer)

    case = relationship("Case", back_populates="messages")
