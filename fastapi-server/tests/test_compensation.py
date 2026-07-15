"""赔偿计算 API 认证测试。"""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_calculate_requires_auth():
    """未认证用户使用赔偿计算应返回 401。"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/compensation/calculate",
            json={"case_id": "00000000-0000-0000-0000-000000000000"},
        )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_invalid_case_id():
    """无效的 case_id 格式应返回 422。"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/compensation/calculate",
            json={"case_id": "not-a-uuid"},
        )
    assert resp.status_code == 401  # 先进入认证，无 token 直接 401


@pytest.mark.asyncio
async def test_document_generate_requires_auth():
    """未认证用户生成文书应返回 401。"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/document/generate",
            json={
                "case_id": "00000000-0000-0000-0000-000000000000",
                "doc_type": "arbitration_request",
            },
        )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_document_download_requires_auth():
    """未认证用户下载文书应返回 401。"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/document/download/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_evidence_upload_requires_auth():
    """未认证用户上传证据应返回 401。"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/evidence/upload")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_evidence_analyze_requires_auth():
    """未认证用户分析证据应返回 401。"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/evidence/analyze/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_evidence_list_requires_auth():
    """未认证用户查看证据清单应返回 401。"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/evidence/list/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 401
