"""管理后台 API。"""
import uuid

from fastapi import APIRouter, HTTPException
from sqlalchemy import func, select

from app.database import AsyncSessionLocal
from app.models.case import Case
from app.models.order import Order
from app.models.user import User
from app.schemas.admin import AdminCaseSummary, AdminUserInfo, DashboardStats

router = APIRouter(prefix="/api/admin", tags=["管理后台"])


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard():
    """管理后台数据面板。"""
    async with AsyncSessionLocal() as db:
        total_users = (await db.execute(select(func.count(User.id)))).scalar() or 0
        total_cases = (await db.execute(select(func.count(Case.id)))).scalar() or 0
        total_rev = (await db.execute(
            select(func.coalesce(func.sum(Order.amount), 0)).where(Order.status == "paid")
        )).scalar()
        total_orders = (await db.execute(
            select(func.count(Order.id)).where(Order.status == "paid")
        )).scalar() or 0

        return DashboardStats(
            total_users=total_users,
            total_cases=total_cases,
            total_orders=total_orders,
            total_revenue=float(total_rev),
            active_today=0,
            new_users_today=0,
        )


@router.get("/users", response_model=list[AdminUserInfo])
async def list_users(page: int = 1, page_size: int = 20):
    """用户列表。"""
    async with AsyncSessionLocal() as db:
        offset = (page - 1) * page_size
        result = await db.execute(
            select(User).order_by(User.created_at.desc()).offset(offset).limit(page_size)
        )
        users = result.scalars().all()

        items = []
        for u in users:
            cnt = (await db.execute(select(func.count(Case.id)).where(Case.user_id == u.id))).scalar() or 0
            items.append(AdminUserInfo(
                id=str(u.id), nickname=u.nickname,
                phone=u.phone[:3] + "****" + u.phone[-4:] if u.phone else None,
                role=u.role, is_vip=u.is_vip, case_count=cnt, created_at=u.created_at,
            ))
        return items


@router.get("/users/{user_id}", response_model=AdminUserInfo)
async def get_user_detail(user_id: str):
    """用户详情。"""
    try:
        uid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(400, "无效的用户 ID")
    async with AsyncSessionLocal() as db:
        u_result = await db.execute(select(User).where(User.id == uid))
        u = u_result.scalar_one_or_none()
        if not u:
            raise HTTPException(404, "用户不存在")
        cnt = (await db.execute(select(func.count(Case.id)).where(Case.user_id == u.id))).scalar() or 0
        return AdminUserInfo(
            id=str(u.id), nickname=u.nickname,
            phone=u.phone[:3] + "****" + u.phone[-4:] if u.phone else None,
            role=u.role, is_vip=u.is_vip, case_count=cnt, created_at=u.created_at,
        )


@router.post("/users/{user_id}/toggle-vip")
async def toggle_user_vip(user_id: str):
    """手动开通/关闭 VIP。"""
    try:
        uid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(400, "无效的用户 ID")
    async with AsyncSessionLocal() as db:
        u_result = await db.execute(select(User).where(User.id == uid))
        user = u_result.scalar_one_or_none()
        if not user:
            raise HTTPException(404, "用户不存在")
        user.is_vip = not user.is_vip
        await db.commit()
        return {"success": True, "is_vip": user.is_vip}


@router.get("/cases", response_model=list[AdminCaseSummary])
async def list_all_cases(page: int = 1, page_size: int = 20):
    """所有案件列表。"""
    async with AsyncSessionLocal() as db:
        offset = (page - 1) * page_size
        result = await db.execute(
            select(Case).order_by(Case.created_at.desc()).offset(offset).limit(page_size)
        )
        cases = result.scalars().all()

        items = []
        for c in cases:
            u_result = await db.execute(select(User).where(User.id == c.user_id))
            u = u_result.scalar_one_or_none()
            items.append(AdminCaseSummary(
                id=str(c.id), user_nickname=u.nickname if u else None,
                title=c.title, stage=c.stage, risk_level=c.risk_level,
                created_at=c.created_at,
            ))
        return items


@router.get("/cases/{case_id}")
async def get_case_detail(case_id: str):
    """案件详情（含消息和证据）。"""
    try:
        cid = uuid.UUID(case_id)
    except ValueError:
        raise HTTPException(400, "无效的案件 ID")
    async with AsyncSessionLocal() as db:
        case_result = await db.execute(select(Case).where(Case.id == cid))
        case = case_result.scalar_one_or_none()
        if not case:
            raise HTTPException(404, "案件不存在")

        from app.models.message import CaseMessage
        msg_result = await db.execute(
            select(CaseMessage).where(CaseMessage.case_id == case.id).order_by(CaseMessage.created_at)
        )
        messages = [{
            "id": str(m.id), "role": m.role, "content": m.content,
            "msg_type": m.msg_type, "created_at": m.created_at.isoformat(),
        } for m in msg_result.scalars().all()]

        user = None
        if case.user_id:
            u_result = await db.execute(select(User).where(User.id == case.user_id))
            user = u_result.scalar_one_or_none()

        return {
            "id": str(case.id), "title": case.title, "stage": case.stage,
            "risk_level": case.risk_level, "profile": case.profile,
            "total_claim_min": str(case.total_claim_min) if case.total_claim_min is not None else None,
            "total_claim_max": str(case.total_claim_max) if case.total_claim_max is not None else None,
            "user": {"id": str(user.id), "nickname": user.nickname} if user else None,
            "messages": messages,
            "created_at": case.created_at.isoformat(),
            "updated_at": case.updated_at.isoformat() if case.updated_at else None,
        }
