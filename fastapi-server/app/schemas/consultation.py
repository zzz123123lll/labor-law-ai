"""对话咨询 Pydantic 模型。"""
from pydantic import BaseModel


class ChatRequest(BaseModel):
    case_id: str | None = None
    message: str
    skip_collection: bool = False  # 跳过信息采集，强制执行分析
