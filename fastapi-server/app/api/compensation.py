"""赔偿计算 API：AI 赔偿计算器。"""
import logging
import uuid

from fastapi import APIRouter, HTTPException, Request
from sqlalchemy import select

from app.agents.base import AgentContext
from app.database import AsyncSessionLocal
from app.models.case import Case
from app.models.compensation import CompensationReport
from app.schemas.compensation import CompensationRequest, CompensationResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/compensation", tags=["赔偿计算"])


@router.post("/calculate", status_code=201)
async def calculate_compensation(
    req: CompensationRequest,
    request: Request,
):
    """调 CompensationCalcAgent 计算赔偿，保存结果到 compensation_reports。"""
    try:
        case_uuid = uuid.UUID(req.case_id)
    except ValueError as err:
        raise HTTPException(status_code=400, detail="无效的 case_id 格式") from err

    async with AsyncSessionLocal() as db:
        # 查询案件（不校验所有权）
        result = await db.execute(
            select(Case).where(Case.id == case_uuid)
        )
        case = result.scalar_one_or_none()
        if case is None:
            raise HTTPException(status_code=404, detail="案件不存在")

        case_profile = case.profile or {}

        # 获取 CompensationCalcAgent
        registry = getattr(request.app.state, "agent_registry", None)
        if registry is None:
            raise HTTPException(status_code=500, detail="Agent 注册表未初始化")
        agent = registry.get("compensation")
        if agent is None:
            raise HTTPException(status_code=500, detail="赔偿计算 Agent 未注册")

        # 构建上下文
        ctx = AgentContext(
            case_profile=case_profile,
            user_message="请根据我的个人信息计算可主张的赔偿金额。",
        )

        # 执行 Agent
        try:
            result = await agent.run(ctx)
        except Exception as e:
            logger.exception("赔偿计算 Agent 执行失败")
            raise HTTPException(status_code=500, detail=f"AI 计算失败: {str(e)}") from e

        # 解析赔偿项（启发式）
        items, total_min, total_max = _parse_compensation_result(result.content)

        # 保存结果
        report = CompensationReport(
            case_id=case_uuid,
            items=items,
            total_min=total_min,
            total_max=total_max,
            calculation=result.content,
        )
        db.add(report)
        await db.commit()
        await db.refresh(report)

        return CompensationResponse(
            id=str(report.id),
            items=report.items,
            total_min=float(report.total_min),
            total_max=float(report.total_max),
            calculation=report.calculation,
            created_at=report.created_at.isoformat(),
        )


# ─── 内部函数 ────────────────────────────────────────────────


def _parse_compensation_result(content: str) -> tuple[list, float, float]:
    """从 Agent 输出中解析赔偿项和金额范围。

    返回 (items, total_min, total_max)。
    """
    import re

    items = []
    total_min = 0.0
    total_max = 0.0

    # 提取表格行中的金额
    for line in content.split('\n'):
        line = line.strip()
        if not line.startswith('|') or not line.endswith('|'):
            continue
        parts = [p.strip() for p in line.split('|')]
        # 过滤表头和分隔行
        if len(parts) < 5:
            continue
        if all(p in ('', '-', '---', '----------') for p in parts[1:-1]):
            continue
        if '项目' in parts[1] or '赔偿项目' in parts[1]:
            continue

        category = parts[1] if len(parts) > 1 else ''
        min_str = parts[2] if len(parts) > 2 else ''
        max_str = parts[3] if len(parts) > 3 else ''
        basis = parts[4] if len(parts) > 4 else ''

        # 解析金额
        min_val = _extract_amount(min_str)
        max_val = _extract_amount(max_str)

        if category and (min_val or max_val):
            items.append({
                "category": category,
                "amount_min": min_val,
                "amount_max": max_val,
                "basis": basis.strip(),
            })

    # 尝试提取合计
    total_match = re.search(r'合计[：:]\s*¥?\s*([\d,]+(?:\.\d{1,2})?)', content)
    if total_match:
        total_min = float(total_match.group(1).replace(',', ''))

    total_max = total_min

    # 如果表格中有多个项，计算总和
    if items:
        sum_min = sum(item.get("amount_min", 0) or 0 for item in items)
        sum_max = sum(item.get("amount_max", 0) or 0 for item in items)
        if sum_min > 0 or sum_max > 0:
            total_min = sum_min
            total_max = sum_max

    return items, total_min, total_max


def _extract_amount(text: str) -> float:
    """从文本中提取金额数值。"""
    import re
    if not text or text == '-':
        return 0.0
    text = text.replace(',', '').replace('，', '')
    match = re.search(r'¥?\s*([\d]+(?:\.\d{1,2})?)', text)
    if match:
        return float(match.group(1))
    # 尝试纯数字
    match = re.search(r'(\d+(?:\.\d{1,2})?)', text)
    if match:
        return float(match.group(1))
    return 0.0
