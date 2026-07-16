"""AI 咨询对话 API 测试。"""
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


def _parse_sse(text: str) -> list[dict]:
    events = []
    for chunk in text.strip().split("\n\n"):
        chunk = chunk.strip()
        if chunk.startswith("data: "):
            events.append(json.loads(chunk[len("data: "):]))
    return events


async def _setup_db():
    """创建内存测试数据库并返回会话工厂。"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    return engine, factory


@pytest.mark.asyncio
async def test_chat_requires_auth():
    """未认证用户调用 chat 应返回 401。"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/consultation/chat", json={"message": "被辞退了怎么办"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_history_requires_auth():
    """未认证用户查看历史应返回 401。"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/consultation/00000000-0000-0000-0000-000000000000/history")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_chat_creates_case():
    """未提供 case_id 时自动创建案件，新案件无 profile 返回信息采集表单。"""
    engine, factory = await _setup_db()

    async with factory() as db:
        user_id = uuid.uuid4()
        user = User(id=user_id, wechat_openid="test_creates_case")
        db.add(user)
        await db.commit()

    token = create_access_token(str(user_id))

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
        assert events[0]["type"] == "form_collect"
        assert "province" in events[0]["fields"]
        assert "monthly_salary" in events[0]["fields"]
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_chat_returns_form_when_profile_incomplete():
    """已有部分 profile 时只追问缺失字段。"""
    engine, factory = await _setup_db()

    async with factory() as db:
        user_id = uuid.uuid4()
        user = User(id=user_id, wechat_openid="test_incomplete")
        db.add(user)
        await db.commit()

        case = Case(user_id=user_id, title="劳动纠纷", profile={"province": "广东"})
        db.add(case)
        await db.commit()
        case_id = str(case.id)

    token = create_access_token(str(user_id))

    try:
        with pytest.MonkeyPatch().context() as mp:
            mp.setattr("app.api.consultation.AsyncSessionLocal", factory)

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.post(
                    "/api/consultation/chat",
                    json={"message": "公司拖欠工资怎么办", "case_id": case_id},
                    headers={"Authorization": f"Bearer {token}"},
                )

        assert resp.status_code == 200
        events = _parse_sse(resp.text)
        assert events[0]["type"] == "form_collect"
        assert "province" not in events[0].get("fields", [])
        for field in ("city", "hire_date", "monthly_salary"):
            assert field in events[0]["fields"], f"缺失字段 {field}"
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_chat_returns_agent_result():
    """profile 完整时跳过表单，进入 Agent 路由分支，流式返回 done。"""
    engine, factory = await _setup_db()

    async with factory() as db:
        user_id = uuid.uuid4()
        user = User(id=user_id, wechat_openid="test_agent_result")
        db.add(user)
        await db.commit()

        case = Case(
            user_id=user_id,
            title="劳动纠纷",
            profile={"province": "广东", "city": "深圳", "hire_date": "2024-03", "monthly_salary": "8000"},
        )
        db.add(case)
        await db.commit()
        case_id = str(case.id)

    token = create_access_token(str(user_id))
    # 设空 agent_registry，profile 完整时走到 agent 路由但不执行真实 agent
    app.state.agent_registry = {}

    try:
        with pytest.MonkeyPatch().context() as mp:
            mp.setattr("app.api.consultation.AsyncSessionLocal", factory)
            mp.setattr("app.agents.router.IntentRouter.route", classmethod(lambda cls, text: []))

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.post(
                    "/api/consultation/chat",
                    json={"message": "被辞退了怎么办", "case_id": case_id},
                    headers={"Authorization": f"Bearer {token}"},
                )

        assert resp.status_code == 200
        events = _parse_sse(resp.text)
        for e in events:
            assert e["type"] != "form_collect", "profile 完整时不应返回表单"
        assert events[-1]["type"] == "done"
    finally:
        await engine.dispose()
