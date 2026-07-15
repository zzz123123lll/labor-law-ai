"""Agent 基类。"""
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

import httpx

from app.legal_engine.law_store import LawArticle, LawStore
from app.legal_engine.case_store import Precedent, CaseStore
from app.config import settings


@dataclass
class AgentContext:
    """Agent 执行上下文。"""
    case_profile: dict = field(default_factory=dict)
    user_message: str = ""
    conversation_history: list[dict] = field(default_factory=list)


@dataclass
class AgentResult:
    """Agent 执行结果。"""
    content: str  # Markdown
    law_refs: list[dict] = field(default_factory=list)  # [{law, article, content}]
    msg_type: str = "text"  # text | report | law_ref


class BaseAgent(ABC):
    """AI Agent 基类。每个子类实现 _build_prompt 定义自己的 Prompt。"""

    name: str = "base"

    def __init__(self, law_store: LawStore, case_store: CaseStore):
        self.law_store = law_store
        self.case_store = case_store

    @abstractmethod
    def search_laws(self, ctx: AgentContext) -> list[LawArticle]:
        """定义需要检索哪些法律条文。"""
        ...

    @abstractmethod
    def build_system_prompt(self, laws: list[LawArticle], precedents: list[Precedent]) -> str:
        """构建 System Prompt。"""
        ...

    async def run(self, ctx: AgentContext) -> AgentResult:
        """执行 Agent：检索法律 → 拼接 Prompt → 调 LLM → 解析结果。"""
        # 1. 检索
        laws = self.search_laws(ctx)
        precedents = self.case_store.search([])

        # 2. 构建 Prompt
        system_prompt = self.build_system_prompt(laws, precedents)
        messages = [
            {"role": "system", "content": system_prompt},
            *ctx.conversation_history[-10:],  # 最近10轮
            {"role": "user", "content": self._build_user_message(ctx)},
        ]

        # 3. 调用 DeepSeek API
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{settings.DEEPSEEK_BASE_URL}/v1/chat/completions",
                headers={"Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}"},
                json={
                    "model": "deepseek-chat",
                    "messages": messages,
                    "temperature": 0.3,
                    "max_tokens": 4096,
                },
            )
        data = resp.json()

        if "choices" not in data:
            return AgentResult(
                content=f"AI 服务暂时不可用，请稍后重试。\n\n> 免责声明：本分析不替代律师正式法律意见。",
                msg_type="error",
            )

        content = data["choices"][0]["message"]["content"]

        # 4. 拼接免责声明
        content += "\n\n---\n\n> ⚠️ 本分析基于公开法律法规，不替代律师正式法律意见。涉及重大权益请咨询专业律师。"

        # 5. 提取引用的法条
        law_refs = [
            {"law": la.law, "article": la.article, "content": la.content[:100]}
            for la in laws
        ]

        return AgentResult(content=content, law_refs=law_refs)

    def _build_user_message(self, ctx: AgentContext) -> str:
        """构建用户消息。"""
        parts = []
        if ctx.case_profile:
            parts.append(f"## 用户信息\n{ctx.case_profile}")
        parts.append(f"## 用户问题\n{ctx.user_message}")
        return "\n\n".join(parts)
