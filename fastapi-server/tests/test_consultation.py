"""AI 咨询对话 API 认证测试。"""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_chat_requires_auth():
    """未认证用户调用 chat 应返回 401。"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/consultation/chat",
            json={"message": "被辞退了怎么办"},
        )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_history_requires_auth():
    """未认证用户查看对话历史应返回 401。"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(
            "/api/consultation/00000000-0000-0000-0000-000000000000/history",
        )
    assert resp.status_code == 401
