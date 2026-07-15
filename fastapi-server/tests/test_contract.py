"""合同审查 API 认证 + 功能测试。"""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_upload_requires_auth():
    """未认证用户上传合同应返回 401。"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/contract/upload")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_review_requires_auth():
    """未认证用户发起审查应返回 401。"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/contract/review/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_report_requires_auth():
    """未认证用户查看报告应返回 401。"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/contract/report/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 401
