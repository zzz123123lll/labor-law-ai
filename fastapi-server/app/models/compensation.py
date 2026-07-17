"""赔偿计算报告模型。"""
import uuid

from sqlalchemy import JSON, ForeignKey, Numeric, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class CompensationReport(Base, TimestampMixin):
    __tablename__ = "compensation_reports"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("cases.id"))
    items: Mapped[list] = mapped_column(JSON)  # [{category, amount, basis, law}]
    total_min: Mapped[float] = mapped_column(Numeric(12, 2))
    total_max: Mapped[float] = mapped_column(Numeric(12, 2))
    calculation: Mapped[str | None] = mapped_column(Text)

    case = relationship("Case", back_populates="compensation_reports")
