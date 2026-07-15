"""合同审查记录模型。"""
from sqlalchemy import ForeignKey, Integer, JSON, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid

from app.models.base import Base, TimestampMixin


class ContractReview(Base, TimestampMixin):
    __tablename__ = "contract_reviews"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("cases.id"))
    file_url: Mapped[str] = mapped_column(String(512))
    ocr_text: Mapped[str | None] = mapped_column(Text)
    score: Mapped[int | None] = mapped_column(Integer)  # 0-100
    risk_level: Mapped[str | None] = mapped_column(String(8))
    findings: Mapped[list | None] = mapped_column(JSON)  # [{clause, risk, law_ref, problem, suggestion}]
    full_report: Mapped[str | None] = mapped_column(Text)

    case = relationship("Case", back_populates="contract_reviews")
