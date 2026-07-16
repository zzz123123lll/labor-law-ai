"""AI 咨询对话 API（核心 SSE 流式接口）。"""
import json
import uuid as uuid_lib
import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select

from app.database import AsyncSessionLocal, get_db
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


@router.post("/chat")
async def chat(
    req: ChatRequest,
    request: Request,
):
    """SSE 流式 AI 对话。不依赖 get_db 注入，手动管理会话以支持流式返回。"""
    # 从 token 解析用户
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        raise HTTPException(401, "未提供认证令牌")
    try:
        payload = decode_token(token)
        if payload.get("type") == "refresh":
            raise HTTPException(401, "请使用 access token")
        user_id = payload["sub"]
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(401, "无效的认证令牌")

    async with AsyncSessionLocal() as db:
        user_result = await db.execute(select(User).where(User.id == uuid_lib.UUID(user_id)))
        user = user_result.scalar_one_or_none()
        if not user:
            raise HTTPException(401, "用户不存在")

        # 获取或创建案件
        if req.case_id:
            try:
                case_uuid = uuid_lib.UUID(req.case_id)
            except (ValueError, AttributeError):
                raise HTTPException(400, "案件ID格式无效")
            case_result = await db.execute(
                select(Case).where(Case.id == case_uuid, Case.user_id == user.id)
            )
            case = case_result.scalar_one_or_none()
            if not case:
                raise HTTPException(404, "案件不存在")
        else:
            case = Case(user_id=user.id, title="新案件")
            db.add(case)

        # 保存用户消息
        user_msg = CaseMessage(
            case_id=case.id, role="user", content=req.message
        )
        db.add(user_msg)
        await db.commit()
        await db.refresh(case)

        profile = case.profile or {}
        missing = _check_missing_fields(profile)

        if missing and not req.skip_collection:
            return StreamingResponse(
                _stream_form_collection(missing, case.id),
                media_type="text/event-stream",
            )

        # AI Router 意图分发
        agent_names = IntentRouter.route(req.message)

        # 获取历史消息
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

        registry = request.app.state.agent_registry

        return StreamingResponse(
            _stream_agent_responses(agent_names, profile, req.message, history, registry, case.id),
            media_type="text/event-stream",
        )


@router.get("/{case_id}/history")
async def get_history(case_id: str, request: Request):
    """获取案件历史消息。"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        raise HTTPException(401, "未提供认证令牌")
    try:
        payload = decode_token(token)
    except Exception:
        raise HTTPException(401, "无效的认证令牌")

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(CaseMessage)
            .where(CaseMessage.case_id == uuid_lib.UUID(case_id))
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


def _check_missing_fields(profile: dict) -> list[str]:
    required = ["province", "city", "hire_date", "monthly_salary"]
    return [f for f in required if f not in profile or not profile[f]]


async def _stream_form_collection(missing: list[str], case_id):
    field_labels = {
        "province": "工作所在省份",
        "city": "工作所在城市",
        "hire_date": "入职时间（如 2024-03）",
        "monthly_salary": "月工资（税前）",
    }
    questions = [field_labels.get(f, f) for f in missing]
    yield f"data: {json.dumps({'type': 'form_collect', 'fields': missing, 'questions': questions, 'case_id': str(case_id)}, ensure_ascii=False)}\n\n"
    yield f"data: {json.dumps({'type': 'done'})}\n\n"


async def _stream_agent_responses(
    agent_names: list[str],
    profile: dict,
    message: str,
    history: list[dict],
    registry,
    case_id,
):
    ctx = AgentContext(case_profile=profile, user_message=message, conversation_history=history)

    for name in agent_names:
        agent = registry.get(name)
        if not agent:
            continue

        try:
            result = await agent.run(ctx)
        except Exception as e:
            from app.agents.base import AgentResult
            result = AgentResult(
                content=f"分析出错: {str(e)}\n\n> 免责声明：本分析不替代律师正式法律意见",
                msg_type="error",
            )

        # 保存 AI 消息到数据库
        async with AsyncSessionLocal() as db:
            ai_msg = CaseMessage(
                case_id=case_id,
                role="assistant",
                content=result.content,
                msg_type=result.msg_type,
                metadata_={"law_refs": result.law_refs, "agent": name},
            )
            db.add(ai_msg)
            await db.commit()

        yield f"data: {json.dumps({'type': 'agent_result', 'agent': name, 'content': result.content, 'law_refs': result.law_refs}, ensure_ascii=False)}\n\n"

    yield f"data: {json.dumps({'type': 'done'})}\n\n"
