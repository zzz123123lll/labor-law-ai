"""认证 API 路由。"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.auth import (
    WechatLoginRequest, BindPhoneRequest, TokenResponse, UserInfo,
)
from app.utils.security import create_access_token, create_refresh_token, encrypt_phone
from app.config import settings

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/wechat-login", response_model=TokenResponse)
async def wechat_login(req: WechatLoginRequest, db: AsyncSession = Depends(get_db)):
    """微信扫码登录，code 换取 openid。"""
    # 调微信开放平台 API
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(
            "https://api.weixin.qq.com/sns/oauth2/access_token",
            params={
                "appid": settings.WECHAT_APP_ID,
                "secret": settings.WECHAT_APP_SECRET,
                "code": req.code,
                "grant_type": "authorization_code",
            },
        )
    wx_data = resp.json()
    if "errcode" in wx_data:
        raise HTTPException(status_code=400, detail=f"微信登录失败: {wx_data['errmsg']}")

    openid = wx_data["openid"]

    # 查找或创建用户
    result = await db.execute(select(User).where(User.wechat_openid == openid))
    user = result.scalar_one_or_none()
    if user is None:
        user = User(wechat_openid=openid)
        db.add(user)
        await db.commit()
        await db.refresh(user)

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserInfo.model_validate(user),
    )


@router.post("/bind-phone")
async def bind_phone(
    req: BindPhoneRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """绑定手机号（首次登录后强制调用）。"""
    # TODO: 验证短信验证码
    current_user.phone = encrypt_phone(req.phone)
    await db.commit()
    return {"success": True}


@router.get("/me", response_model=UserInfo)
async def get_me(current_user: User = Depends(get_current_user)):
    """获取当前用户信息。"""
    return UserInfo.model_validate(current_user)
