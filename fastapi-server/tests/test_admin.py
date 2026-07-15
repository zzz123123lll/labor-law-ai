"""管理后台 API 测试（admin 接口暂不强制鉴权，测试可直接调用）。"""
import uuid
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.main import app
from app.models.base import Base
from app.models.user import User
from app.models.case import Case
from app.models.order import Order
from app.api.admin import router as admin_router


# ─── 辅助函数 ────────────────────────────────────────────────────


async def _setup_db():
    """创建内存 SQLite 数据库并建表。"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    return engine, async_sessionmaker(engine, expire_on_commit=False)


async def _create_test_data(factory):
    """插入测试数据：用户、案件、订单。"""
    async with factory() as db:
        user1 = User(
            id=uuid.uuid4(),
            wechat_openid="admin_user_1",
            nickname="测试用户1",
            phone="13800138001",
            role="user",
            is_vip=False,
        )
        user2 = User(
            id=uuid.uuid4(),
            wechat_openid="admin_user_2",
            nickname="测试用户2",
            phone="13800138002",
            role="user",
            is_vip=True,
        )
        db.add_all([user1, user2])
        await db.commit()
        await db.refresh(user1)
        await db.refresh(user2)

        case1 = Case(
            id=uuid.uuid4(),
            user_id=user1.id,
            title="劳动纠纷案-1",
            stage="consultation",
            risk_level="high",
            profile={"province": "广东", "city": "深圳"},
            total_claim_min=10000,
            total_claim_max=50000,
        )
        case2 = Case(
            id=uuid.uuid4(),
            user_id=user2.id,
            title="劳动纠纷案-2",
            stage="arbitration",
            risk_level="medium",
            profile={"province": "北京"},
            total_claim_min=20000,
            total_claim_max=80000,
        )
        db.add_all([case1, case2])
        await db.commit()

        order1 = Order(
            id=uuid.uuid4(),
            user_id=user1.id,
            plan_id="monthly",
            amount=29.90,
            status="paid",
        )
        order2 = Order(
            id=uuid.uuid4(),
            user_id=user2.id,
            plan_id="yearly",
            amount=199.00,
            status="paid",
        )
        db.add_all([order1, order2])
        await db.commit()

        return {"user1": user1, "user2": user2, "case1": case1, "case2": case2}


# ─── 测试用例 ────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_dashboard():
    """GET /api/admin/dashboard 返回统计数据。"""
    engine, factory = await _setup_db()
    test_data = await _create_test_data(factory)

    with pytest.MonkeyPatch().context() as mp:
        mp.setattr("app.api.admin.AsyncSessionLocal", factory)
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/admin/dashboard")

    assert resp.status_code == 200
    data = resp.json()
    assert data["total_users"] == 2
    assert data["total_cases"] == 2
    assert data["total_orders"] == 2
    assert data["total_revenue"] == pytest.approx(228.90, 0.01)
    assert "active_today" in data
    assert "new_users_today" in data

    await engine.dispose()


@pytest.mark.asyncio
async def test_list_users():
    """GET /api/admin/users 返回用户列表。"""
    engine, factory = await _setup_db()
    test_data = await _create_test_data(factory)

    with pytest.MonkeyPatch().context() as mp:
        mp.setattr("app.api.admin.AsyncSessionLocal", factory)
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/admin/users")

    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    # 验证脱敏手机号
    phones = [u["phone"] for u in data if u["phone"]]
    for p in phones:
        assert "****" in p
        assert len(p) == 11  # 138****8001
    # 验证字段
    first = data[0]
    assert "id" in first
    assert "nickname" in first
    assert "role" in first
    assert "is_vip" in first
    assert "case_count" in first
    assert "created_at" in first

    await engine.dispose()


@pytest.mark.asyncio
async def test_get_user_detail():
    """GET /api/admin/users/{user_id} 返回用户详情。"""
    engine, factory = await _setup_db()
    test_data = await _create_test_data(factory)

    with pytest.MonkeyPatch().context() as mp:
        mp.setattr("app.api.admin.AsyncSessionLocal", factory)
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get(f"/api/admin/users/{test_data['user1'].id}")

    assert resp.status_code == 200
    data = resp.json()
    assert data["nickname"] == "测试用户1"
    assert data["role"] == "user"
    assert data["is_vip"] is False
    assert data["case_count"] >= 1

    await engine.dispose()


@pytest.mark.asyncio
async def test_get_user_detail_not_found():
    """GET /api/admin/users/{user_id} 不存在的用户返回 404。"""
    engine, factory = await _setup_db()
    await _create_test_data(factory)

    with pytest.MonkeyPatch().context() as mp:
        mp.setattr("app.api.admin.AsyncSessionLocal", factory)
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get(f"/api/admin/users/{uuid.uuid4()}")

    assert resp.status_code == 404

    await engine.dispose()


@pytest.mark.asyncio
async def test_toggle_vip():
    """POST /api/admin/users/{user_id}/toggle-vip 切换 VIP 状态。"""
    engine, factory = await _setup_db()
    test_data = await _create_test_data(factory)
    user1 = test_data["user1"]

    with pytest.MonkeyPatch().context() as mp:
        mp.setattr("app.api.admin.AsyncSessionLocal", factory)
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # 第一次切换：False → True
            resp1 = await client.post(f"/api/admin/users/{user1.id}/toggle-vip")
            assert resp1.status_code == 200
            assert resp1.json()["is_vip"] is True

            # 第二次切换：True → False
            resp2 = await client.post(f"/api/admin/users/{user1.id}/toggle-vip")
            assert resp2.status_code == 200
            assert resp2.json()["is_vip"] is False

    # 验证数据库持久化
    async with factory() as db:
        from sqlalchemy import select
        result = await db.execute(select(User).where(User.id == user1.id))
        user = result.scalar_one()
        assert user.is_vip is False

    await engine.dispose()


@pytest.mark.asyncio
async def test_toggle_vip_not_found():
    """POST /api/admin/users/{user_id}/toggle-vip 不存在的用户返回 404。"""
    engine, factory = await _setup_db()

    with pytest.MonkeyPatch().context() as mp:
        mp.setattr("app.api.admin.AsyncSessionLocal", factory)
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(f"/api/admin/users/{uuid.uuid4()}/toggle-vip")

    assert resp.status_code == 404

    await engine.dispose()


@pytest.mark.asyncio
async def test_list_all_cases():
    """GET /api/admin/cases 返回所有案件列表。"""
    engine, factory = await _setup_db()
    test_data = await _create_test_data(factory)

    with pytest.MonkeyPatch().context() as mp:
        mp.setattr("app.api.admin.AsyncSessionLocal", factory)
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/admin/cases")

    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    # 验证字段
    case = data[0]
    assert "id" in case
    assert "user_nickname" in case
    assert "title" in case
    assert "stage" in case
    assert "risk_level" in case
    assert "created_at" in case

    await engine.dispose()


@pytest.mark.asyncio
async def test_get_case_detail():
    """GET /api/admin/cases/{case_id} 返回案件详情（含消息）。"""
    engine, factory = await _setup_db()
    test_data = await _create_test_data(factory)
    case1 = test_data["case1"]

    with pytest.MonkeyPatch().context() as mp:
        mp.setattr("app.api.admin.AsyncSessionLocal", factory)
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get(f"/api/admin/cases/{case1.id}")

    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == str(case1.id)
    assert data["title"] == "劳动纠纷案-1"
    assert data["stage"] == "consultation"
    assert data["risk_level"] == "high"
    assert "profile" in data
    assert "messages" in data
    assert "user" in data
    assert data["user"]["nickname"] == "测试用户1"

    await engine.dispose()


@pytest.mark.asyncio
async def test_get_case_detail_not_found():
    """GET /api/admin/cases/{case_id} 不存在的案件返回 404。"""
    engine, factory = await _setup_db()

    with pytest.MonkeyPatch().context() as mp:
        mp.setattr("app.api.admin.AsyncSessionLocal", factory)
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get(f"/api/admin/cases/{uuid.uuid4()}")

    assert resp.status_code == 404

    await engine.dispose()
