"""证据分析 API：上传证据文件 + OCR + AI 分析 + 证据清单。"""
import uuid
import os
import logging

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select

import aiofiles

from app.database import AsyncSessionLocal
from app.utils.security import decode_token
from app.models.user import User
from app.models.case import Case
from app.models.evidence import EvidenceFile
from app.schemas.evidence import EvidenceUploadResponse, EvidenceListResponse
from app.agents.base import AgentContext

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/evidence", tags=["证据分析"])
security = HTTPBearer()

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 安全限制
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_TYPES = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".pdf", ".doc", ".docx"}

FILE_TYPE_LABELS: dict[str, str] = {
    ".png": "image", ".jpg": "image", ".jpeg": "image", ".gif": "image",
    ".bmp": "image", ".webp": "image", ".pdf": "pdf",
    ".doc": "document", ".docx": "document",
}


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
        result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
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


def _validate_file(file: UploadFile):
    """验证文件类型和大小。"""
    ext = os.path.splitext(file.filename or "file.bin")[1].lower()
    if ext not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail=f"不支持的文件类型: {ext}。允许: {', '.join(sorted(ALLOWED_TYPES))}")

    # 检查文件大小（读取到内存验证——UploadFile 无 size 属性但可以读前几个字节）
    # fastapi 的 UploadFile 在完整接收后可通过 .size 获取
    if hasattr(file, "size") and file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail=f"文件过大。最大允许 10MB，当前 {file.size / 1024 / 1024:.1f}MB")


async def _save_upload(file: UploadFile) -> tuple[str, str]:
    """保存上传文件，返回 (file_url, file_path)。"""
    ext = os.path.splitext(file.filename or "file")[1].lower()
    if ext not in ALLOWED_TYPES:
        ext = ".bin"
    filename = f"{uuid.uuid4()}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    async with aiofiles.open(filepath, 'wb') as f:
        await f.write(await file.read())
    return f"/uploads/{filename}", filepath


def _infer_file_type(filename: str) -> str:
    """根据扩展名推断文件类型。"""
    ext = os.path.splitext(filename)[1].lower()
    if ext in (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"):
        return "image"
    elif ext == ".pdf":
        return "pdf"
    else:
        return "screenshot"


@router.post("/upload", status_code=201)
async def upload_evidence(
    request: Request,
    file: UploadFile = File(...),
    case_id: str = ...,
    current_user: User = Depends(_get_current_user),
):
    """上传证据文件，验证案件归属，OCR 提取文本。"""
    _validate_file(file)
    try:
        case_uuid = uuid.UUID(case_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的 case_id 格式")

    async with AsyncSessionLocal() as db:
        # 验证案件归属
        result = await db.execute(
            select(Case).where(
                Case.id == case_uuid,
                Case.user_id == current_user.id,
            )
        )
        case = result.scalar_one_or_none()
        if case is None:
            raise HTTPException(status_code=404, detail="案件不存在")

    file_url, file_path = await _save_upload(file)
    file_type = _infer_file_type(file.filename or "file.bin")
    ocr_text = await _ocr_file(file_path)

    async with AsyncSessionLocal() as db:
        evidence = EvidenceFile(
            case_id=case_uuid,
            file_url=file_url,
            file_type=file_type,
            ocr_text=ocr_text,
        )
        db.add(evidence)
        await db.commit()
        await db.refresh(evidence)

        return EvidenceUploadResponse(
            id=str(evidence.id),
            file_url=evidence.file_url,
            file_type=evidence.file_type,
            ocr_text=evidence.ocr_text,
            created_at=evidence.created_at.isoformat(),
        )


@router.post("/analyze/{file_id}")
async def analyze_evidence(
    file_id: str,
    request: Request,
    current_user: User = Depends(_get_current_user),
):
    """调 EvidenceAnalyzeAgent 执行 AI 分析，更新 evidence.analysis。"""
    try:
        evidence_uuid = uuid.UUID(file_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的 file_id 格式")

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(EvidenceFile).where(EvidenceFile.id == evidence_uuid)
        )
        evidence = result.scalar_one_or_none()
        if evidence is None:
            raise HTTPException(status_code=404, detail="证据记录不存在")

        # 验证 case 归属
        case_result = await db.execute(
            select(Case).where(
                Case.id == evidence.case_id,
                Case.user_id == current_user.id,
            )
        )
        case = case_result.scalar_one_or_none()
        if case is None:
            raise HTTPException(status_code=404, detail="案件不存在或不属于当前用户")

        case_profile = case.profile or {}

        # 获取 EvidenceAnalyzeAgent
        registry = getattr(request.app.state, "agent_registry", None)
        if registry is None:
            raise HTTPException(status_code=500, detail="Agent 注册表未初始化")
        agent = registry.get("evidence")
        if agent is None:
            raise HTTPException(status_code=500, detail="证据分析 Agent 未注册")

        # 构建上下文
        ocr_content = evidence.ocr_text or "[无 OCR 内容]"
        ctx = AgentContext(
            case_profile=case_profile,
            user_message=f"请分析以下证据内容，评估证据效力并给出补充建议：\n\n{ocr_content}",
        )

        # 执行 Agent
        try:
            result = await agent.run(ctx)
        except Exception as e:
            logger.exception("证据分析 Agent 执行失败")
            raise HTTPException(status_code=500, detail=f"AI 分析失败: {str(e)}")

        # 更新分析结果
        evidence.analysis = {
            "content": result.content,
            "law_refs": result.law_refs,
        }
        await db.commit()
        await db.refresh(evidence)

        return EvidenceListResponse(
            id=str(evidence.id),
            file_url=evidence.file_url,
            file_type=evidence.file_type,
            ocr_text=evidence.ocr_text,
            analysis=evidence.analysis,
            created_at=evidence.created_at.isoformat(),
        )


@router.get("/list/{case_id}")
async def list_evidence(
    case_id: str,
    current_user: User = Depends(_get_current_user),
):
    """返回指定案件的证据清单。"""
    try:
        case_uuid = uuid.UUID(case_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的 case_id 格式")

    async with AsyncSessionLocal() as db:
        # 验证案件归属
        result = await db.execute(
            select(Case).where(
                Case.id == case_uuid,
                Case.user_id == current_user.id,
            )
        )
        case = result.scalar_one_or_none()
        if case is None:
            raise HTTPException(status_code=404, detail="案件不存在")

        # 查询证据
        result = await db.execute(
            select(EvidenceFile)
            .where(EvidenceFile.case_id == case_uuid)
            .order_by(EvidenceFile.created_at)
        )
        evidence_list = result.scalars().all()

        return [
            EvidenceListResponse(
                id=str(e.id),
                file_url=e.file_url,
                file_type=e.file_type,
                ocr_text=e.ocr_text,
                analysis=e.analysis,
                created_at=e.created_at.isoformat(),
            )
            for e in evidence_list
        ]
