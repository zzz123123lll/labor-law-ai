"""案件 CRUD API 测试。"""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_create_case_requires_auth():
    """未认证用户创建案件应返回 401。"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/cases", json={"title": "测试"})
    assert resp.status_code == 401  # 未认证


@pytest.mark.asyncio
async def test_list_cases_requires_auth():
    """未认证用户查看案件列表应返回 401。"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/cases")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_case_requires_auth():
    """未认证用户查看案件详情应返回 401。"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/cases/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_update_case_requires_auth():
    """未认证用户更新案件应返回 401。"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.patch("/api/cases/00000000-0000-0000-0000-000000000000", json={"title": "新标题"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_delete_case_requires_auth():
    """未认证用户删除案件应返回 401。"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.delete("/api/cases/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 401
