"""认证相关 Pydantic 模型。"""
from pydantic import BaseModel


class WechatLoginRequest(BaseModel):
    code: str


class BindPhoneRequest(BaseModel):
    phone: str
    sms_code: str


class UserInfo(BaseModel):
    id: str
    nickname: str | None
    avatar_url: str | None
    phone: str | None
    role: str
    is_vip: bool

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserInfo
