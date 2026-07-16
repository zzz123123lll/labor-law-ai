"""案件相关 Pydantic 模型。"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CaseCreate(BaseModel):
    title: str = "新案件"


class CaseUpdate(BaseModel):
    title: str | None = None
    stage: str | None = None
    profile: dict | None = None


class CaseSummary(BaseModel):
    id: str
    title: str
    stage: str
    risk_level: str | None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True)


class CaseDetail(BaseModel):
    id: str
    user_id: str
    title: str
    stage: str
    status: str
    profile: dict
    risk_level: str | None
    total_claim_min: float | None
    total_claim_max: float | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True)
