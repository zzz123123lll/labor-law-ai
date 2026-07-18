"""仲裁委查询 API。"""
import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/api/arbitration", tags=["仲裁委查询"])

# 启动时加载数据
_data: list[dict] = []


def _load():
    global _data
    if _data:
        return
    data_path = Path(__file__).parent.parent / "legal_engine" / "data" / "arbitration_committees.json"
    if data_path.exists():
        _data = json.loads(data_path.read_text(encoding="utf-8"))


@router.get("/search")
async def search_arbitration(q: str = Query(min_length=1, description="城市名或省份名")):
    """根据城市名或省份名搜索仲裁委。"""
    _load()
    results = [c for c in _data if q in c.get("city", "") or q in c.get("province", "")]
    if not results:
        # 模糊匹配
        results = [c for c in _data if any(q in v for v in c.values() if isinstance(v, str))]
    return results[:5]


@router.get("/by-city/{city}")
async def get_by_city(city: str):
    """精确查询城市仲裁委。"""
    _load()
    for c in _data:
        if c.get("city") == city:
            return c
    raise HTTPException(status_code=404, detail=f"未找到 {city} 的仲裁委信息")
