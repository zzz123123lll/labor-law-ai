"""本地设置 API——AI Key 等运行时配置。"""
import json
from pathlib import Path

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/settings", tags=["设置"])

import sys

if getattr(sys, 'frozen', False):
    CONFIG_PATH = Path(sys.executable).parent / "data" / "app_settings.json"
else:
    CONFIG_PATH = Path(__file__).parent.parent.parent / "app_settings.json"


class AISettings(BaseModel):
    llm_api_key: str = Field(default="", max_length=256)


def _read_config() -> dict:
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _write_config(config: dict):
    CONFIG_PATH.write_text(
        json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8"
    )


@router.get("")
async def get_settings():
    """获取当前设置。"""
    config = _read_config()
    return {
        "llm_api_key": config.get("llm_api_key", ""),
        "llm_provider": config.get("llm_provider", "deepseek"),
        "llm_model": config.get("llm_model", "deepseek-chat"),
    }


@router.post("/ai-key")
async def save_ai_key(body: AISettings):
    """保存 AI Key。"""
    config = _read_config()
    config["llm_api_key"] = body.llm_api_key
    _write_config(config)
    # 清除 LLM 适配器单例缓存，让下次请求用新 key
    import app.ai.adapters as adapters

    adapters._adapter = None
    return {"success": True}
