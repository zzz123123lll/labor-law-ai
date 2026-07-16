"""文书生成 API：AI 起草法律文书 + Markdown/PDF 下载。"""
import uuid
import logging
import tempfile
import os

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.utils.security import decode_token
from app.models.user import User
from app.models.case import Case
from app.models.document import GeneratedDocument
from app.schemas.document import DocumentGenerateRequest, DocumentResponse
from app.agents.base import AgentContext

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/document", tags=["文书生成"])
security = HTTPBearer()

# 合法文书类型
VALID_DOC_TYPES = {"arbitration_request", "complaint_letter", "evidence_list"}


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


def _doc_type_label(doc_type: str) -> str:
    """返回文书类型的中文名称。"""
    labels = {
        "arbitration_request": "劳动仲裁申请书",
        "complaint_letter": "投诉信",
        "evidence_list": "证据清单",
    }
    return labels.get(doc_type, doc_type)


@router.post("/generate", status_code=201)
async def generate_document(
    req: DocumentGenerateRequest,
    request: Request,
    current_user: User = Depends(_get_current_user),
):
    """调 DocumentDraftAgent 生成文书，保存到 generated_documents。"""
    if req.doc_type not in VALID_DOC_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文书类型: {req.doc_type}，支持: {', '.join(VALID_DOC_TYPES)}",
        )

    try:
        case_uuid = uuid.UUID(req.case_id)
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

        case_profile = case.profile or {}

        # 获取 DocumentDraftAgent
        registry = getattr(request.app.state, "agent_registry", None)
        if registry is None:
            raise HTTPException(status_code=500, detail="Agent 注册表未初始化")
        agent = registry.get("document_draft")
        if agent is None:
            raise HTTPException(status_code=500, detail="文书生成 Agent 未注册")

        # 构建上下文（根据 doc_type 调整提示）
        doc_type_labels = {
            "arbitration_request": "劳动仲裁申请书",
            "complaint_letter": "投诉信",
            "evidence_list": "证据清单",
        }
        doc_label = doc_type_labels.get(req.doc_type, req.doc_type)
        ctx = AgentContext(
            case_profile=case_profile,
            user_message=f"请根据我的案件信息，起草一份 {doc_label}。请严格按照法律文书的格式输出。",
        )

        # 执行 Agent
        try:
            result = await agent.run(ctx)
        except Exception as e:
            logger.exception("文书生成 Agent 执行失败")
            raise HTTPException(status_code=500, detail=f"文书生成失败: {str(e)}")

        # 生成标题
        title = _doc_type_label(req.doc_type)

        # 保存到数据库
        doc = GeneratedDocument(
            case_id=case_uuid,
            doc_type=req.doc_type,
            title=title,
            content=result.content,
            status="draft",
        )
        db.add(doc)
        await db.commit()
        await db.refresh(doc)

        return DocumentResponse(
            id=str(doc.id),
            doc_type=doc.doc_type,
            title=doc.title,
            content=doc.content,
            status=doc.status,
            created_at=doc.created_at.isoformat(),
        )


@router.get("/download/{id}")
async def download_document(
    id: str,
    current_user: User = Depends(_get_current_user),
):
    """返回文书的 Markdown 内容（PDF 生成后期再做）。"""
    try:
        doc_uuid = uuid.UUID(id)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的 id 格式")

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(GeneratedDocument).where(GeneratedDocument.id == doc_uuid)
        )
        doc = result.scalar_one_or_none()
        if doc is None:
            raise HTTPException(status_code=404, detail="文书不存在")

        return DocumentResponse(
            id=str(doc.id),
            doc_type=doc.doc_type,
            title=doc.title,
            content=doc.content,
            status=doc.status,
            created_at=doc.created_at.isoformat(),
        )


@router.get("/download/{id}/pdf")
async def download_pdf(
    id: str,
    current_user: User = Depends(_get_current_user),
):
    """下载文书的 PDF 版本（格式化排版 + 页眉页脚）。"""
    try:
        doc_uuid = uuid.UUID(id)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的 id 格式")

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(GeneratedDocument).where(GeneratedDocument.id == doc_uuid)
        )
        doc = result.scalar_one_or_none()
        if doc is None:
            raise HTTPException(status_code=404, detail="文书不存在")

    try:
        pdf_path = _markdown_to_pdf(doc.title, doc.content)
    except Exception as e:
        logger.exception("PDF 生成失败")
        raise HTTPException(status_code=500, detail=f"PDF 生成失败: {str(e)}。请使用 Markdown 下载代替。")

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"{doc.title}.pdf",
        background=None,
    )


def _markdown_to_pdf(title: str, markdown_content: str) -> str:
    """将 Markdown 文书转换为格式化 PDF。

    尝试顺序：WeasyPrint（需系统 GTK）→ xhtml2pdf（纯 Python）。
    均不可用时抛出异常，建议使用 Markdown 下载。
    """
    import markdown as md_lib

    html_body = md_lib.markdown(markdown_content, extensions=["extra", "tables"])

    HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="utf-8">
<style>
  body {{ font-family: "PingFang SC","Microsoft YaHei","SimSun",sans-serif; font-size: 12pt; line-height: 2; color: #1A1A1A; padding: 2cm; }}
  h1 {{ font-size: 18pt; text-align: center; border-bottom: 2px solid #1E40AF; padding-bottom: 12pt; }}
  h2 {{ font-size: 15pt; margin-top: 24pt; color: #1E40AF; }}
  h3 {{ font-size: 13pt; }}
  table {{ width: 100%; border-collapse: collapse; margin: 12pt 0; }}
  th, td {{ border: 1px solid #E5E7EB; padding: 8pt; text-align: left; font-size: 11pt; }}
  th {{ background: #F3F4F6; }}
  blockquote {{ border-left: 3px solid #1E40AF; padding-left: 12pt; color: #666; }}
  .disclaimer {{ font-size: 9pt; color: #999; border-top: 1px solid #E5E7EB; margin-top: 36pt; padding-top: 12pt; }}
</style></head>
<body>{body}<div class="disclaimer">本文书由 AI 辅助生成，不替代律师正式法律意见。生成时间：{now}</div></body>
</html>"""

    html = HTML_TEMPLATE.format(
        title=title, body=html_body, now=_now_str(),
    )

    # 尝试 1: WeasyPrint
    try:
        from weasyprint import HTML as WHTML
        tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        WHTML(string=html).write_pdf(tmp.name)
        tmp.close()
        return tmp.name
    except (OSError, ImportError):
        pass

    # 尝试 2: xhtml2pdf
    try:
        from xhtml2pdf import pisa
        tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        with open(tmp.name, "wb") as f:
            pisa.CreatePDF(html, dest=f)
        return tmp.name
    except ImportError:
        pass

    raise RuntimeError(
        "PDF 生成需要安装 WeasyPrint（Linux/Mac）或 xhtml2pdf（跨平台）。"
        "请运行: pip install xhtml2pdf"
    )


def _now_str() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

