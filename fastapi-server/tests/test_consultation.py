"""AI 咨询对话 API 认证 + 功能测试。"""
import json
import uuid
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.main import app
from app.models.base import Base
from app.models.user import User
from app.models.case import Case
from app.utils.security import create_access_token
from app.api.consultation import _get_current_user


# ─── 认证层测试（无需数据库） ────────────────────────────────────────


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


# ─── 功能测试（需内存 SQLite 模拟数据库） ──────────────────────────────


def _parse_sse(text: str) -> list[dict]:
    """解析 SSE 文本，返回事件 data 列表。"""
    events = []
    for chunk in text.strip().split("\n\n"):
        chunk = chunk.strip()
        if chunk.startswith("data: "):
            events.append(json.loads(chunk[len("data: "):]))
    return events


@pytest.mark.asyncio
async def test_chat_creates_case():
    """未提供 case_id 时自动创建案件，profile 为空返回信息采集表单。"""
    # ── 创建内存 SQLite 数据库 ──
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)

    # ── 创建测试用户 ──
    async with factory() as db:
        user_id = uuid.uuid4()
        user = User(id=user_id, wechat_openid="test_creates_case")
        db.add(user)
        await db.commit()
        await db.refresh(user)

    token = create_access_token(str(user_id))
    mock_user = User(id=user_id, wechat_openid="test_creates_case")

    app.dependency_overrides[_get_current_user] = lambda: mock_user
    try:
        with pytest.MonkeyPatch().context() as mp:
            mp.setattr("app.api.consultation.AsyncSessionLocal", factory)
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.post(
                    "/api/consultation/chat",
                    json={"message": "被辞退了怎么办"},
                    headers={"Authorization": f"Bearer {token}"},
                )

        assert resp.status_code == 200
        assert resp.headers.get("content-type", "").startswith("text/event-stream")

        events = _parse_sse(resp.text)
        assert len(events) >= 1
        # 第一个事件应为 form_collect（新案件无 profile）
        assert events[0]["type"] == "form_collect"
        assert "fields" in events[0]
        assert "case_id" in events[0]
        # 验证返回了必填字段
        assert "province" in events[0]["fields"]
        assert "monthly_salary" in events[0]["fields"]
    finally:
        app.dependency_overrides.pop(_get_current_user, None)
        await engine.dispose()


@pytest.mark.asyncio
async def test_chat_returns_form_when_profile_incomplete():
    """profile 不完整时返回信息采集表单，已有字段不再追问。"""
    # ── 创建内存 SQLite 数据库 ──
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)

    # ── 创建测试用户 + 部分 profile 的 case ──
    async with factory() as db:
        user_id = uuid.uuid4()
        user = User(id=user_id, wechat_openid="test_incomplete")
        db.add(user)
        await db.commit()
        await db.refresh(user)

        case = Case(
            user_id=user_id,
            title="劳动纠纷",
            profile={"province": "广东"},
        )
        db.add(case)
        await db.commit()
        await db.refresh(case)
        case_id = str(case.id)

    token = create_access_token(str(user_id))
    mock_user = User(id=user_id, wechat_openid="test_incomplete")

    app.dependency_overrides[_get_current_user] = lambda: mock_user
    try:
        with pytest.MonkeyPatch().context() as mp:
            mp.setattr("app.api.consultation.AsyncSessionLocal", factory)
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.post(
                    "/api/consultation/chat",
                    json={
                        "message": "公司拖欠工资怎么办",
                        "case_id": case_id,
                    },
                    headers={"Authorization": f"Bearer {token}"},
                )

        assert resp.status_code == 200
        assert resp.headers.get("content-type", "").startswith("text/event-stream")

        events = _parse_sse(resp.text)
        assert len(events) >= 1
        assert events[0]["type"] == "form_collect"
        # province 已有，不应在 missing 中
        assert "province" not in events[0].get("fields", [])
        # 缺失字段应全部返回
        for field in ("city", "hire_date", "monthly_salary"):
            assert field in events[0]["fields"], f"缺失字段 {field} 未在表单中返回"
    finally:
        app.dependency_overrides.pop(_get_current_user, None)
        await engine.dispose()


# ─── TODO（后续连接真实数据库后补充） ─────────────────────────────────
"""
以下功能测试需要完整的数据库和 AI Agent 环境，当前无法完整模拟：

1. test_chat_history_requires_auth  — 已覆盖（test_history_requires_auth）
2. test_chat_with_complete_profile → 验证 profile 完整时走 AI 分析而非表单采集
3. test_chat_history_full          → 验证历史接口返回消息列表
4. test_chat_skip_collection       → 验证 skip_collection=True 跳过表单
"""
