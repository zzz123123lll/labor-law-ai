"""案件模型。"""
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, JSON, Numeric, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid

from app.models.base import Base, TimestampMixin


class Case(Base, TimestampMixin):
    __tablename__ = "cases"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(128))
    stage: Mapped[str] = mapped_column(String(16), default="consultation")
    status: Mapped[str] = mapped_column(String(16), default="active")  # active | archived | deleted
    profile: Mapped[dict] = mapped_column(JSON, default=dict)
    risk_level: Mapped[str | None] = mapped_column(String(8))  # low | medium | high | critical
    total_claim_min: Mapped[float | None] = mapped_column(Numeric(12, 2))
    total_claim_max: Mapped[float | None] = mapped_column(Numeric(12, 2))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="cases")
    messages = relationship("CaseMessage", back_populates="case", order_by="CaseMessage.created_at")
    evidence_files = relationship("EvidenceFile", back_populates="case")
    contract_reviews = relationship("ContractReview", back_populates="case")
    compensation_reports = relationship("CompensationReport", back_populates="case")
    generated_documents = relationship("GeneratedDocument", back_populates="case")
