"""合同审查 API：上传合同文件 + AI 审查 + 报告查询。

由于 get_db 尚未实现，当前在模块内创建临时数据库引擎与会话工厂。
后续 Task 连接主数据库路由后可迁移至 app.state 统一管理。
"""
import uuid
import os
import logging

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select

import aiofiles

from app.config import settings
from app.utils.security import decode_token
from app.models.user import User
from app.models.case import Case
from app.models.contract_review import ContractReview
from app.schemas.contract import ContractReviewResponse
from app.agents.base import AgentContext

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/contract", tags=["合同审查"])
security = HTTPBearer()

# 临时数据库会话工厂
_engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(_engine, expire_on_commit=False)

# 上传目录
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


async def _get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    """认证依赖：解析 JWT 并返回当前用户。"""
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


async def _ocr_file(file_path: str) -> str:
    """OCR 文件提取文本，PaddleOCR 不可用时返回占位。"""
    try:
        from paddleocr import PaddleOCR
        ocr = PaddleOCR(lang='ch')
        result = ocr.ocr(file_path)
        lines = []
        for page in result:
            if page:
                for line in page:
                    lines.append(line[1][0])
        return '\n'.join(lines)
    except ImportError:
        return "[OCR 引擎未安装，已保存原始文件]"
    except Exception as e:
        return f"[OCR 失败: {str(e)}]"


async def _save_upload(file: UploadFile) -> tuple[str, str]:
    """保存上传文件，返回 (file_url, file_path)。"""
    ext = os.path.splitext(file.filename or "file")[1] or ".bin"
    filename = f"{uuid.uuid4()}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    async with aiofiles.open(filepath, 'wb') as f:
        await f.write(await file.read())
    return f"/uploads/{filename}", filepath


@router.post("/upload", status_code=201)
async def upload_contract(
    request: Request,
    file: UploadFile = File(...),
    case_id: str | None = None,
    current_user: User = Depends(_get_current_user),
):
    """上传合同文件，执行 OCR 提取文本，创建审查记录。"""
    file_url, file_path = await _save_upload(file)
    ocr_text = await _ocr_file(file_path)

    async with AsyncSessionLocal() as db:
        # 如果指定了 case_id，验证归属
        review_case_id = None
        if case_id:
            try:
                case_uuid = uuid.UUID(case_id)
            except ValueError:
                raise HTTPException(status_code=400, detail="无效的 case_id 格式")
            result = await db.execute(
                select(Case).where(
                    Case.id == case_uuid,
                    Case.user_id == current_user.id,
                )
            )
            case = result.scalar_one_or_none()
            if case is None:
                raise HTTPException(status_code=404, detail="案件不存在")
            review_case_id = case_uuid

        review = ContractReview(
            case_id=review_case_id,
            file_url=file_url,
            ocr_text=ocr_text,
        )
        db.add(review)
        await db.commit()
        await db.refresh(review)

        return ContractReviewResponse(
            id=str(review.id),
            score=review.score,
            risk_level=review.risk_level,
            findings=review.findings,
            full_report=review.full_report,
            created_at=review.created_at.isoformat(),
        )


@router.post("/review/{file_id}")
async def review_contract(
    file_id: str,
    request: Request,
    current_user: User = Depends(_get_current_user),
):
    """调 ContractReviewAgent 执行 AI 审查，更新 findings/score/risk_level/full_report。"""
    try:
        review_uuid = uuid.UUID(file_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的 file_id 格式")

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(ContractReview).where(ContractReview.id == review_uuid)
        )
        review = result.scalar_one_or_none()
        if review is None:
            raise HTTPException(status_code=404, detail="审查记录不存在")

        # 获取关联案件的 profile
        case_profile = {}
        if review.case_id:
            case_result = await db.execute(
                select(Case).where(
                    Case.id == review.case_id,
                    Case.user_id == current_user.id,
                )
            )
            case = case_result.scalar_one_or_none()
            if case is None:
                raise HTTPException(status_code=404, detail="案件不存在或不属于当前用户")
            case_profile = case.profile or {}

        # 获取 ContractReviewAgent
        registry = getattr(request.app.state, "agent_registry", None)
        if registry is None:
            raise HTTPException(status_code=500, detail="Agent 注册表未初始化")
        agent = registry.get("contract_review")
        if agent is None:
            raise HTTPException(status_code=500, detail="合同审查 Agent 未注册")

        # 构建上下文
        ocr_content = review.ocr_text or "[无 OCR 内容]"
        ctx = AgentContext(
            case_profile={**case_profile, "contract_text": ocr_content},
            user_message=f"请审查以下劳动合同内容，识别风险条款并给出评分：\n\n{ocr_content}",
        )

        # 执行 Agent
        try:
            result = await agent.run(ctx)
        except Exception as e:
            logger.exception("合同审查 Agent 执行失败")
            raise HTTPException(status_code=500, detail=f"AI 分析失败: {str(e)}")

        # 解析结果中的评分和风险等级（简单启发式解析）
        score, risk_level = _parse_review_result(result.content)

        # 更新审查记录
        review.full_report = result.content
        review.score = score
        review.risk_level = risk_level
        await db.commit()
        await db.refresh(review)

        return ContractReviewResponse(
            id=str(review.id),
            score=review.score,
            risk_level=review.risk_level,
            findings=review.findings,
            full_report=review.full_report,
            created_at=review.created_at.isoformat(),
        )


@router.get("/report/{id}")
async def get_contract_report(
    id: str,
    current_user: User = Depends(_get_current_user),
):
    """返回审查报告。"""
    try:
        review_uuid = uuid.UUID(id)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的 id 格式")

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(ContractReview).where(ContractReview.id == review_uuid)
        )
        review = result.scalar_one_or_none()
        if review is None:
            raise HTTPException(status_code=404, detail="审查记录不存在")

        return ContractReviewResponse(
            id=str(review.id),
            score=review.score,
            risk_level=review.risk_level,
            findings=review.findings,
            full_report=review.full_report,
            created_at=review.created_at.isoformat(),
        )


# ─── 内部函数 ────────────────────────────────────────────────


def _parse_review_result(content: str) -> tuple[int | None, str | None]:
    """从 Agent 输出中解析评分和风险等级。

    启发式解析，不依赖 LLM 结构化输出，支持多种格式。
    """
    score = None
    risk_level = None

    # 尝试提取评分
    import re
    score_match = re.search(r'(\d+)\s*\/?\s*[1１0０0]', content)
    if score_match:
        raw = int(score_match.group(1))
        # 如果是 5 分制，转为 100 分制
        if raw <= 5:
            score = raw * 20
        else:
            score = min(raw, 100)

    # 如果没有匹配到评分，尝试找 "X/5" 模式
    if score is None:
        score_match = re.search(r'(?:评分|合规性|综合)[：:]\s*★*☆*\s*(\d+)\s*/\s*5', content)
        if score_match:
            raw = int(score_match.group(1))
            score = raw * 20

    # 尝试提取风险等级
    if re.search(r'高风险|危险|违法', content):
        risk_level = "high"
    elif re.search(r'中风险|中等|部分合规', content):
        risk_level = "medium"
    elif re.search(r'低风险|基本合规|合规', content) and not re.search(r'高风险|中风险', content):
        risk_level = "low"

    return score, risk_level
