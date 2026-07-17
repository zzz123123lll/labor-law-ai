"""证据文件模型。"""
import uuid

from sqlalchemy import JSON, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class EvidenceFile(Base, TimestampMixin):
    __tablename__ = "evidence_files"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("cases.id"), index=True)
    file_url: Mapped[str] = mapped_column(String(512))
    file_type: Mapped[str] = mapped_column(String(16))  # image | pdf | screenshot
    ocr_text: Mapped[str | None] = mapped_column(Text)
    analysis: Mapped[dict | None] = mapped_column(JSON)

    case = relationship("Case", back_populates="evidence_files")
