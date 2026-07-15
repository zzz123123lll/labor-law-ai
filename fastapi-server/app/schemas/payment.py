from pydantic import BaseModel
from datetime import datetime


class PlanInfo(BaseModel):
    plan_id: str
    name: str
    price: float
    period: str  # monthly | yearly | forever
    features: list[str]


class OrderResponse(BaseModel):
    id: str
    plan_id: str
    amount: float
    status: str
    qr_code_url: str | None = None  # 微信支付二维码
    created_at: datetime

    class Config:
        from_attributes = True


class SubscriptionResponse(BaseModel):
    id: str
    plan_id: str
    status: str
    start_at: datetime | None
    end_at: datetime | None

    class Config:
        from_attributes = True
