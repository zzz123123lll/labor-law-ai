"""认证 API 路由——本地工具模式，仅保留状态接口。"""
from fastapi import APIRouter

router = APIRouter(prefix="/api/auth", tags=["状态"])


@router.get("/status")
async def auth_status():
    return {"authenticated": False, "message": "本地工具模式，无需登录"}
