"""Agent 基类——所有 AI Agent 的抽象父类。"""
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

from app.ai.base import ChatMessage, LLMError
from app.ai.adapters import get_llm
from app.legal_engine.law_store import LawArticle, LawStore
from app.legal_engine.case_store import Precedent, CaseStore


@dataclass
class AgentContext:
    """Agent 执行上下文。"""
    case_profile: dict = field(default_factory=dict)
    user_message: str = ""
    conversation_history: list[dict] = field(default_factory=list)


@dataclass
class AgentResult:
    """Agent 执行结果。"""
    content: str
    law_refs: list[dict] = field(default_factory=list)
    msg_type: str = "text"


class BaseAgent(ABC):
    """AI Agent 基类。

    子类只需实现 search_laws() 和 build_system_prompt()，
    run() 自动处理：法律检索 → Prompt 拼接 → LLM 调用 → 结果返回。
    """

    name: str = "base"

    def __init__(self, law_store: LawStore, case_store: CaseStore):
        self.law_store = law_store
        self.case_store = case_store

    @abstractmethod
    def search_laws(self, ctx: AgentContext) -> list[LawArticle]:
        """需要检索哪些法律条文。"""
        ...

    @abstractmethod
    def build_system_prompt(self, laws: list[LawArticle], precedents: list[Precedent]) -> str:
        """构建 System Prompt。"""
        ...

    async def run(self, ctx: AgentContext) -> AgentResult:
        """执行 Agent：检索 → Prompt → LLM → 结果。"""
        # 1. 检索法律与案例
        laws = self.search_laws(ctx)
        precedents = self.case_store.search([])

        # 2. 构建 Prompt
        system_prompt = self.build_system_prompt(laws, precedents)
        messages = [
            ChatMessage(role="system", content=system_prompt),
            *[ChatMessage(role=m["role"], content=m["content"])
              for m in ctx.conversation_history[-10:]],
            ChatMessage(role="user", content=self._build_user_message(ctx)),
        ]

        # 3. 调 LLM（通过适配器——可替换为任意模型）
        llm = get_llm()
        try:
            result = await llm.chat(messages)
        except LLMError as e:
            return AgentResult(
                content=f"AI 服务调用失败：{str(e)}\n\n> 免责声明：本分析不替代律师正式法律意见。",
                msg_type="error",
            )

        # 4. 拼接免责声明
        content = result.content.strip()
        content += "\n\n---\n\n> ⚠️ 本分析基于公开法律法规，不替代律师正式法律意见。涉及重大权益请咨询专业律师。"

        # 5. 提取引用的法条
        law_refs = [
            {"law": la.law, "article": la.article, "content": la.content[:100]}
            for la in laws
        ]

        return AgentResult(content=content, law_refs=law_refs)

    def _build_user_message(self, ctx: AgentContext) -> str:
        parts = []
        if ctx.case_profile:
            parts.append(f"## 用户信息\n{ctx.case_profile}")
        parts.append(f"## 用户问题\n{ctx.user_message}")
        return "\n\n".join(parts)
