"""管理后台 API 测试——需要管理员认证。"""
import uuid
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.main import app
from app.models.base import Base
from app.models.user import User
from app.models.case import Case
from app.models.order import Order
async def _setup_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    return engine, async_sessionmaker(engine, expire_on_commit=False)


async def _create_test_data(factory) -> dict:
    async with factory() as db:
        admin = User(
            id=uuid.uuid4(), wechat_openid="admin_test", nickname="Admin",
            phone="13800000000", role="admin", is_vip=True,
        )
        user1 = User(
            id=uuid.uuid4(), wechat_openid="test_u1", nickname="测试用户1",
            phone="13800138001", role="user", is_vip=False,
        )
        db.add_all([admin, user1])
        await db.commit()
        await db.refresh(admin), await db.refresh(user1)

        case1 = Case(id=uuid.uuid4(), user_id=user1.id, title="劳动纠纷-1",
                     stage="consultation", risk_level="high",
                     profile={"province": "广东", "city": "深圳"},
                     total_claim_min=10000, total_claim_max=50000)
        db.add(case1)
        await db.commit()

        o = Order(id=uuid.uuid4(), user_id=user1.id, plan_id="monthly", amount=29.90, status="paid")
        db.add(o)
        await db.commit()

        return {"admin": admin, "user1": user1, "case1": case1}


# ─── 测试 ──────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_dashboard():
    engine, factory = await _setup_db()
    data = await _create_test_data(factory)

    try:
        with pytest.MonkeyPatch().context() as mp:
            mp.setattr("app.api.admin.AsyncSessionLocal", factory)
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.get("/api/admin/dashboard")
            assert resp.status_code == 200
            d = resp.json()
            assert d["total_users"] >= 1
            assert d["total_orders"] == 1
            assert d["total_revenue"] == pytest.approx(29.90, 0.01)
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_list_users():
    engine, factory = await _setup_db()
    data = await _create_test_data(factory)

    try:
        with pytest.MonkeyPatch().context() as mp:
            mp.setattr("app.api.admin.AsyncSessionLocal", factory)
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.get("/api/admin/users")
            assert resp.status_code == 200
            users = resp.json()
            assert len(users) >= 1
            for u in users:
                if u.get("phone") and "13800138001" in u["phone"].replace("*", ""):
                    continue
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_get_user_detail():
    engine, factory = await _setup_db()
    data = await _create_test_data(factory)

    try:
        with pytest.MonkeyPatch().context() as mp:
            mp.setattr("app.api.admin.AsyncSessionLocal", factory)
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.get(f"/api/admin/users/{data['user1'].id}")
            assert resp.status_code == 200
            assert resp.json()["nickname"] == "测试用户1"
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_get_user_detail_not_found():
    engine, factory = await _setup_db()
    data = await _create_test_data(factory)

    try:
        with pytest.MonkeyPatch().context() as mp:
            mp.setattr("app.api.admin.AsyncSessionLocal", factory)
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.get(f"/api/admin/users/{uuid.uuid4()}")
            assert resp.status_code == 404
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_toggle_vip():
    engine, factory = await _setup_db()
    data = await _create_test_data(factory)

    try:
        with pytest.MonkeyPatch().context() as mp:
            mp.setattr("app.api.admin.AsyncSessionLocal", factory)
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp1 = await client.post(f"/api/admin/users/{data['user1'].id}/toggle-vip")
                assert resp1.status_code == 200
                assert resp1.json()["is_vip"] is True

                resp2 = await client.post(f"/api/admin/users/{data['user1'].id}/toggle-vip")
                assert resp2.status_code == 200
                assert resp2.json()["is_vip"] is False
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_list_all_cases():
    engine, factory = await _setup_db()
    data = await _create_test_data(factory)

    try:
        with pytest.MonkeyPatch().context() as mp:
            mp.setattr("app.api.admin.AsyncSessionLocal", factory)
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.get("/api/admin/cases")
            assert resp.status_code == 200
            cases = resp.json()
            assert len(cases) >= 1
            assert "title" in cases[0]
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_get_case_detail():
    engine, factory = await _setup_db()
    data = await _create_test_data(factory)

    try:
        with pytest.MonkeyPatch().context() as mp:
            mp.setattr("app.api.admin.AsyncSessionLocal", factory)
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.get(f"/api/admin/cases/{data['case1'].id}")
            assert resp.status_code == 200
            detail = resp.json()
            assert detail["title"] == "劳动纠纷-1"
            assert detail["risk_level"] == "high"
            assert "messages" in detail
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_get_case_detail_not_found():
    engine, factory = await _setup_db()
    data = await _create_test_data(factory)

    try:
        with pytest.MonkeyPatch().context() as mp:
            mp.setattr("app.api.admin.AsyncSessionLocal", factory)
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.get(f"/api/admin/cases/{uuid.uuid4()}")
            assert resp.status_code == 404
    finally:
        await engine.dispose()
