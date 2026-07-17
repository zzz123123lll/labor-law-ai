"""支付 API 测试。"""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
@pytest.mark.asyncio
async def test_get_plans():
    """获取所有付费方案——应返回 3 个方案。"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/payment/plans")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 3
    plan_ids = {p["plan_id"] for p in data}
    assert plan_ids == {"free", "monthly", "yearly"}


@pytest.mark.asyncio
async def test_create_order_free_plan_fails():
    """免费方案不能创建订单——应返回 400。"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/payment/create-order?plan_id=free")
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_create_order_invalid_plan_fails():
    """无效的方案 ID 创建订单——应返回 400。"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/payment/create-order?plan_id=nonexistent")
    assert resp.status_code == 400
