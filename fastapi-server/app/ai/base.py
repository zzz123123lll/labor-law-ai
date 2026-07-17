"""AI 适配器抽象层。所有 LLM 调用通过此层统一管理，方便替换不同模型。"""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ChatMessage:
    role: str  # system | user | assistant
    content: str


@dataclass
class ChatResult:
    content: str
    model: str = ""
    tokens_used: int = 0


class BaseLLMAdapter(ABC):
    """LLM 适配器基类。实现此接口即可接入任意 AI 模型。"""

    name: str = "base"

    @abstractmethod
    async def chat(self, messages: list[ChatMessage], **kwargs) -> ChatResult:
        """发送对话请求，返回模型回复。"""
        ...


class LLMError(Exception):
    """LLM 调用失败。"""
    pass
