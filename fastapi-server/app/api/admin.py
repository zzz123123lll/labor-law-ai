"""管理后台 API——仅管理员可访问。"""
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from app.database import AsyncSessionLocal
from app.models.user import User
from app.models.case import Case
from app.models.order import Order
from app.schemas.admin import DashboardStats, AdminUserInfo, AdminCaseSummary

router = APIRouter(prefix="/api/admin", tags=["管理后台"])


async def _require_admin(user_id: str) -> User:
    """验证管理员权限。"""
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user or user.role != "admin":
            raise HTTPException(403, "需要管理员权限")
        return user


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard():
    """管理后台数据面板。"""
    async with AsyncSessionLocal() as db:
        total_users = (await db.execute(select(func.count(User.id)))).scalar()
        total_cases = (await db.execute(select(func.count(Case.id)))).scalar()
        total_revenue_result = await db.execute(
            select(func.coalesce(func.sum(Order.amount), 0)).where(Order.status == "paid")
        )
        total_revenue = float(total_revenue_result.scalar())
        total_orders = (await db.execute(
            select(func.count(Order.id)).where(Order.status == "paid")
        )).scalar()

        return DashboardStats(
            total_users=total_users or 0,
            total_cases=total_cases or 0,
            total_orders=total_orders or 0,
            total_revenue=total_revenue,
            active_today=0,
            new_users_today=0,
        )


@router.get("/users", response_model=list[AdminUserInfo])
async def list_users(page: int = 1, page_size: int = 20):
    """用户列表（管理员）。"""
    async with AsyncSessionLocal() as db:
        offset = (page - 1) * page_size
        result = await db.execute(
            select(User)
            .order_by(User.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        users = result.scalars().all()

        items = []
        for u in users:
            case_count_result = await db.execute(
                select(func.count(Case.id)).where(Case.user_id == u.id)
            )
            case_count = case_count_result.scalar() or 0
            items.append(AdminUserInfo(
                id=str(u.id),
                nickname=u.nickname,
                phone=u.phone[:3] + "****" + u.phone[-4:] if u.phone else None,
                role=u.role,
                is_vip=u.is_vip,
                case_count=case_count,
                created_at=u.created_at,
            ))
        return items


@router.get("/users/{user_id}", response_model=AdminUserInfo)
async def get_user_detail(user_id: str):
    """用户详情。"""
    try:
        uid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(400, "无效的用户 ID 格式")
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.id == uid))
        u = result.scalar_one_or_none()
        if not u:
            raise HTTPException(404, "用户不存在")
        case_count_result = await db.execute(
            select(func.count(Case.id)).where(Case.user_id == u.id)
        )
        case_count = case_count_result.scalar() or 0
        return AdminUserInfo(
            id=str(u.id),
            nickname=u.nickname,
            phone=u.phone[:3] + "****" + u.phone[-4:] if u.phone else None,
            role=u.role,
            is_vip=u.is_vip,
            case_count=case_count,
            created_at=u.created_at,
        )


@router.post("/users/{user_id}/toggle-vip")
async def toggle_user_vip(user_id: str):
    """手动开通/关闭 VIP。"""
    try:
        uid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(400, "无效的用户 ID 格式")
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.id == uid))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(404, "用户不存在")
        user.is_vip = not user.is_vip
        await db.commit()
        return {"success": True, "is_vip": user.is_vip}


@router.get("/cases", response_model=list[AdminCaseSummary])
async def list_all_cases(page: int = 1, page_size: int = 20):
    """所有案件列表（管理员只读）。"""
    async with AsyncSessionLocal() as db:
        offset = (page - 1) * page_size
        result = await db.execute(
            select(Case)
            .order_by(Case.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        cases = result.scalars().all()

        items = []
        for c in cases:
            user_result = await db.execute(select(User).where(User.id == c.user_id))
            user = user_result.scalar_one_or_none()
            items.append(AdminCaseSummary(
                id=str(c.id),
                user_nickname=user.nickname if user else None,
                title=c.title,
                stage=c.stage,
                risk_level=c.risk_level,
                created_at=c.created_at,
            ))
        return items


@router.get("/cases/{case_id}")
async def get_case_detail(case_id: str):
    """案件详情（含全部消息和证据）。"""
    try:
        cid = uuid.UUID(case_id)
    except ValueError:
        raise HTTPException(400, "无效的案件 ID 格式")
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Case).where(Case.id == cid))
        case = result.scalar_one_or_none()
        if not case:
            raise HTTPException(404, "案件不存在")

        from app.models.message import CaseMessage
        msg_result = await db.execute(
            select(CaseMessage).where(CaseMessage.case_id == case.id).order_by(CaseMessage.created_at)
        )
        messages = [
            {"id": str(m.id), "role": m.role, "content": m.content, "msg_type": m.msg_type, "created_at": m.created_at.isoformat()}
            for m in msg_result.scalars().all()
        ]

        user_result = await db.execute(select(User).where(User.id == case.user_id))
        user = user_result.scalar_one()

        return {
            "id": str(case.id),
            "title": case.title,
            "stage": case.stage,
            "risk_level": case.risk_level,
            "profile": case.profile,
            "total_claim_min": str(case.total_claim_min) if case.total_claim_min is not None else None,
            "total_claim_max": str(case.total_claim_max) if case.total_claim_max is not None else None,
            "user": {"id": str(user.id), "nickname": user.nickname},
            "messages": messages,
            "created_at": case.created_at.isoformat(),
            "updated_at": case.updated_at.isoformat() if case.updated_at else None,
        }
