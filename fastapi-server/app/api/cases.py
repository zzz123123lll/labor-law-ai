"""案件 CRUD API。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.case import Case
from app.schemas.case import CaseCreate, CaseDetail, CaseSummary, CaseUpdate

router = APIRouter(prefix="/api/cases", tags=["案件"])


@router.post("", response_model=CaseDetail, status_code=201)
async def create_case(
    req: CaseCreate,
    db: AsyncSession = Depends(get_db),
):
    """创建新案件。"""
    case = Case(title=req.title)
    db.add(case)
    await db.commit()
    await db.refresh(case)
    return CaseDetail.model_validate(case)


@router.get("", response_model=list[CaseSummary])
async def list_cases(
    db: AsyncSession = Depends(get_db),
):
    """获取所有案件（排除已删除）。"""
    result = await db.execute(
        select(Case)
        .where(Case.status != "deleted")
        .order_by(Case.updated_at.desc())
    )
    cases = result.scalars().all()
    return [CaseSummary.model_validate(c) for c in cases]


@router.get("/{case_id}", response_model=CaseDetail)
async def get_case(
    case_id: str,
    db: AsyncSession = Depends(get_db),
):
    """获取单个案件详情。"""
    result = await db.execute(select(Case).where(Case.id == case_id))
    case = result.scalar_one_or_none()
    if case is None:
        raise HTTPException(status_code=404, detail="案件不存在")
    return CaseDetail.model_validate(case)


@router.patch("/{case_id}", response_model=CaseDetail)
async def update_case(
    case_id: str,
    req: CaseUpdate,
    db: AsyncSession = Depends(get_db),
):
    """更新案件信息。"""
    result = await db.execute(select(Case).where(Case.id == case_id))
    case = result.scalar_one_or_none()
    if case is None:
        raise HTTPException(status_code=404, detail="案件不存在")

    if req.title is not None:
        case.title = req.title
    if req.stage is not None:
        case.stage = req.stage
    if req.profile is not None:
        case.profile = {**case.profile, **req.profile}

    await db.commit()
    await db.refresh(case)
    return CaseDetail.model_validate(case)


@router.delete("/{case_id}")
async def delete_case(
    case_id: str,
    db: AsyncSession = Depends(get_db),
):
    """软删除案件。"""
    result = await db.execute(select(Case).where(Case.id == case_id))
    case = result.scalar_one_or_none()
    if case is None:
        raise HTTPException(status_code=404, detail="案件不存在")

    case.status = "deleted"
    await db.commit()
    return {"success": True}
