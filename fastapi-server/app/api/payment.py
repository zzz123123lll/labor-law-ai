"""支付 API —— 三档定价 + 订单 + 订阅 + VIP。"""
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.utils.security import decode_token
from app.models.user import User
from app.models.order import Order
from app.models.subscription import Subscription
from app.schemas.payment import PlanInfo, OrderResponse, SubscriptionResponse

router = APIRouter(prefix="/api/payment", tags=["支付"])
security = HTTPBearer()


# ---------------------------------------------------------------------------
# 三档付费方案（硬编码，按设计文档 9.2 节）
# ---------------------------------------------------------------------------
PLANS = [
    PlanInfo(
        plan_id="free",
        name="免费版",
        price=0,
        period="forever",
        features=["AI咨询 5次/天", "基础赔偿计算", "基础违法识别"],
    ),
    PlanInfo(
        plan_id="monthly",
        name="专业版",
        price=29.9,
        period="monthly",
        features=["无限AI咨询", "合同审查 10次/月", "文书PDF下载", "证据分析", "案件管理 20个"],
    ),
    PlanInfo(
        plan_id="yearly",
        name="企业版",
        price=199,
        period="yearly",
        features=["全部专业版功能", "优先响应", "人工复核选项", "无限案件"],
    ),
]


async def _get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    """认证依赖：解析 JWT 并返回当前用户。"""
    try:
        payload = decode_token(credentials.credentials)
        if payload.get("type") == "refresh":
            raise HTTPException(status_code=401, detail="请使用 access token")
        user_id = payload["sub"]
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="无效的认证令牌")

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user is None:
            raise HTTPException(status_code=401, detail="用户不存在")
        return user


@router.get("/plans", response_model=list[PlanInfo])
async def get_plans():
    """获取所有付费方案。"""
    return PLANS


@router.post("/create-order", response_model=OrderResponse)
async def create_order(plan_id: str, current_user: User = Depends(_get_current_user)):
    """创建支付订单。微信支付 Native API → 二维码 URL。

    当前为 mock 实现——微信支付需要企业资质，暂返回占位二维码。
    """
    plan = next((p for p in PLANS if p.plan_id == plan_id), None)
    if not plan or plan.plan_id == "free":
        raise HTTPException(400, "无效的付费方案")

    async with AsyncSessionLocal() as db:
        order = Order(
            user_id=current_user.id,
            plan_id=plan_id,
            amount=plan.price,
            status="pending",
        )
        db.add(order)
        await db.commit()
        await db.refresh(order)

        return OrderResponse(
            id=str(order.id),
            plan_id=order.plan_id,
            amount=plan.price,
            status="pending",
            qr_code_url=f"https://api.qrserver.com/v1/create-qr-code/?data=WXPAY_MOCK_{order.id}",
            created_at=order.created_at,
        )


@router.post("/notify")
async def payment_notify(transaction_id: str, order_id: str):
    """微信支付回调。Mock 实现——直接标记订单为已支付，开通订阅。"""
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Order).where(Order.id == order_id))
        order = result.scalar_one_or_none()
        if not order:
            raise HTTPException(404, "订单不存在")

        order.status = "paid"
        order.wx_transaction_id = transaction_id
        order.paid_at = datetime.now(timezone.utc)

        # 开通 / 续费订阅
        sub_result = await db.execute(
            select(Subscription).where(Subscription.user_id == order.user_id)
        )
        sub = sub_result.scalar_one_or_none()

        now = datetime.now(timezone.utc)
        if order.plan_id == "monthly":
            end_at = now + timedelta(days=30)
        else:
            end_at = now + timedelta(days=365)

        if sub:
            sub.plan_id = order.plan_id
            sub.status = "active"
            sub.start_at = sub.start_at or now
            sub.end_at = max(sub.end_at or now, end_at)
        else:
            sub = Subscription(
                user_id=order.user_id,
                plan_id=order.plan_id,
                status="active",
                start_at=now,
                end_at=end_at,
            )
            db.add(sub)

        # 更新用户 VIP 状态
        user_result = await db.execute(select(User).where(User.id == order.user_id))
        user = user_result.scalar_one()
        user.is_vip = True
        user.vip_expire_at = end_at

        await db.commit()
        return {"success": True, "message": "支付成功，已开通VIP"}


@router.get("/my-subscription", response_model=SubscriptionResponse | None)
async def get_my_subscription(current_user: User = Depends(_get_current_user)):
    """获取当前用户的订阅状态。"""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Subscription).where(Subscription.user_id == current_user.id)
        )
        sub = result.scalar_one_or_none()
        if not sub:
            return None
        return SubscriptionResponse(
            id=str(sub.id),
            plan_id=sub.plan_id,
            status=sub.status,
            start_at=sub.start_at,
            end_at=sub.end_at,
        )
