from pydantic import BaseModel
from datetime import datetime


class DashboardStats(BaseModel):
    total_users: int
    total_cases: int
    total_orders: int
    total_revenue: float
    active_today: int
    new_users_today: int


class AdminUserInfo(BaseModel):
    id: str
    nickname: str | None
    phone: str | None
    role: str
    is_vip: bool
    case_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class AdminCaseSummary(BaseModel):
    id: str
    user_nickname: str | None
    title: str
    stage: str
    risk_level: str | None
    created_at: datetime

    class Config:
        from_attributes = True
