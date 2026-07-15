"""AI 咨询对话 API（核心 SSE 流式接口）。

由于 get_db 尚未实现，当前在模块内创建临时数据库引擎与会话工厂。
后续 Task 连接主数据库路由后可迁移至 app.state 统一管理。
"""
import json
import uuid
import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select

from app.config import settings
from app.utils.security import decode_token
from app.models.user import User
from app.models.case import Case
from app.models.message import CaseMessage
from app.schemas.consultation import ChatRequest
from app.agents.base import AgentContext
from app.agents.router import IntentRouter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/consultation", tags=["AI咨询"])
security = HTTPBearer()

# 临时数据库会话工厂（get_db 存根替代）
_engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(_engine, expire_on_commit=False)


async def _get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    """认证依赖：解析 JWT 并返回当前用户（使用本地会话工厂）。"""
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


@router.post("/chat")
async def chat(
    req: ChatRequest,
    current_user: User = Depends(_get_current_user),
    request: Request = None,
):
    """SSE 流式 AI 对话。

    1. 获取或创建案件
    2. 保存用户消息
    3. 检查 profile 完整度 → 不完整则返回采集表单
    4. IntentRouter 分发 → 逐个执行 Agent → SSE 流式输出
    """
    async with AsyncSessionLocal() as db:
        # ── 1. 获取或创建案件 ──
        if req.case_id:
            result = await db.execute(
                select(Case).where(
                    Case.id == req.case_id,
                    Case.user_id == current_user.id,
                )
            )
            case = result.scalar_one_or_none()
            if case is None:
                raise HTTPException(status_code=404, detail="案件不存在")
        else:
            case = Case(user_id=current_user.id, title="新案件")
            db.add(case)
            await db.commit()
            await db.refresh(case)

        # ── 2. 保存用户消息 ──
        user_msg = CaseMessage(
            case_id=case.id,
            role="user",
            content=req.message,
        )
        db.add(user_msg)
        await db.commit()

        # ── 3. 检查案件 profile 完整度 → 信息采集模式 ──
        profile = case.profile or {}
        missing = _check_missing_fields(profile)
        if missing and not req.skip_collection:
            return StreamingResponse(
                _stream_form_collection(missing, case.id),
                media_type="text/event-stream",
            )

        # ── 4. AI Router 意图分发 ──
        agent_names = IntentRouter.route(req.message)

        # ── 5. 获取最近历史消息 ──
        history_result = await db.execute(
            select(CaseMessage)
            .where(CaseMessage.case_id == case.id)
            .order_by(CaseMessage.created_at)
            .limit(20)
        )
        history = [
            {"role": m.role, "content": m.content}
            for m in history_result.scalars().all()
        ]

    # ── 6. 流式返回 AI 分析（数据库会话已关闭，agent 内自行管理）──
    registry = request.app.state.agent_registry

    return StreamingResponse(
        _stream_agent_responses(
            agent_names, profile, req.message, history, registry, case.id,
        ),
        media_type="text/event-stream",
    )


@router.get("/{case_id}/history")
async def get_history(
    case_id: str,
    current_user: User = Depends(_get_current_user),
):
    """获取指定案件的对话历史。"""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(CaseMessage)
            .join(Case, CaseMessage.case_id == Case.id)
            .where(
                CaseMessage.case_id == case_id,
                Case.user_id == current_user.id,
            )
            .order_by(CaseMessage.created_at)
        )
        messages = result.scalars().all()
        return [
            {
                "id": str(m.id),
                "role": m.role,
                "content": m.content,
                "msg_type": m.msg_type,
                "created_at": m.created_at.isoformat(),
            }
            for m in messages
        ]


# ─── 内部函数 ────────────────────────────────────────────────


def _check_missing_fields(profile: dict) -> list[str]:
    """检查案件信息缺失字段，返回需要追问的字段名列表。"""
    required = ["province", "city", "hire_date", "monthly_salary"]
    return [f for f in required if f not in profile or not profile[f]]


async def _stream_form_collection(
    missing: list[str],
    case_id: uuid.UUID,
):
    """流式输出信息采集表单（字段标签 + case_id）。"""
    field_labels = {
        "province": "工作所在省份",
        "city": "工作所在城市",
        "hire_date": "入职时间（如 2024-03）",
        "monthly_salary": "月工资（税前）",
    }
    questions = [field_labels.get(f, f) for f in missing]
    yield (
        f"data: {json.dumps(
            {
                'type': 'form_collect',
                'fields': missing,
                'questions': questions,
                'case_id': str(case_id),
            },
            ensure_ascii=False,
        )}\n\n"
    )
    yield f"data: {json.dumps({'type': 'done'})}\n\n"


async def _stream_agent_responses(
    agent_names: list[str],
    profile: dict,
    message: str,
    history: list[dict],
    registry,
    case_id: uuid.UUID,
):
    """逐个执行 Agent 并流式输出结果，结果持久化到 case_messages。"""
    ctx = AgentContext(
        case_profile=profile,
        user_message=message,
        conversation_history=history,
    )

    for name in agent_names:
        agent = registry.get(name)
        if agent is None:
            continue

        # 执行 Agent
        try:
            result = await agent.run(ctx)
        except Exception as e:
            result = _error_result(f"分析出错: {e}")

        # 保存 AI 消息（独立数据库会话）
        async with AsyncSessionLocal() as db:
            ai_msg = CaseMessage(
                case_id=case_id,
                role="assistant",
                content=result.content,
                msg_type=result.msg_type,
                metadata_={
                    "law_refs": result.law_refs,
                    "agent": name,
                },
            )
            db.add(ai_msg)
            await db.commit()

        yield (
            f"data: {json.dumps(
                {
                    'type': 'agent_result',
                    'agent': name,
                    'content': result.content,
                    'law_refs': result.law_refs,
                },
                ensure_ascii=False,
            )}\n\n"
        )

    yield f"data: {json.dumps({'type': 'done'})}\n\n"


def _error_result(error_msg: str):
    """构造一个模拟 AgentResult 用于错误处理。"""
    from types import SimpleNamespace
    return SimpleNamespace(
        content=f"{error_msg}\n\n> 免责声明：本分析不替代律师正式法律意见",
        law_refs=[],
        msg_type="error",
    )
