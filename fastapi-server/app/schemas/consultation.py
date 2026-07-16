"""对话咨询 Pydantic 模型。"""
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    case_id: str | None = Field(default=None, max_length=64)
    message: str = Field(min_length=1, max_length=10000)
    skip_collection: bool = False
