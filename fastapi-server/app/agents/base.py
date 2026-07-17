"""Agent 基类——所有 AI Agent 的抽象父类。"""
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from app.ai.adapters import get_llm
from app.ai.base import ChatMessage, LLMError
from app.legal_engine.case_store import CaseStore, Precedent
from app.legal_engine.law_store import LawArticle, LawStore


@dataclass
class AgentContext:
    """Agent 执行上下文。"""
    case_profile: dict = field(default_factory=dict)
    user_message: str = ""
    conversation_history: list[dict] = field(default_factory=list)


@dataclass
class AgentResult:
    """Agent 执行结果。

    包含 Markdown 可读内容（content）和结构化数据（structured），
    结构化数据供下游 Agent 级联消费，无需重新解析 Markdown。
    """
    content: str
    law_refs: list[dict] = field(default_factory=list)
    msg_type: str = "text"
    structured: dict = field(default_factory=dict)
    # structured 示例:
    # {
    #   "violations": [{"type": "拖欠工资", "legal": false, "law_ref": "劳动法第50条"}],
    #   "compensation": {"total_min": 45000, "total_max": 60000, "items": [...]},
    #   "risk_level": "high"
    # }


class BaseAgent(ABC):
    """AI Agent 基类。

    子类只需实现 search_laws() 和 build_system_prompt()，
    run() 自动处理：法律检索 → Prompt 拼接 → LLM 调用 → 结构化解析 → 结果返回。
    """

    name: str = "base"

    # 子类可覆盖：结构化提取模式（Regex → dict）
    _structured_patterns: list[tuple[str, str]] = []

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
        """执行 Agent：检索 → Prompt → LLM → 结构化解析 → 结果。"""
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

        # 5. 提取实际引用的法条（只保留 LLM 回复中真正提到的，不把搜索到的全塞进去）
        law_refs = self._match_cited_laws(result.content, laws)

        # 6. 提取结构化数据（不依赖 LLM function calling——对任意模型有效）
        structured = self._extract_structured(result.content)

        return AgentResult(content=content, law_refs=law_refs, structured=structured)

    @staticmethod
    def _match_cited_laws(response_text: str, searched_laws: list[LawArticle]) -> list[dict]:
        """只返回 LLM 回复中实际引用到的法条，避免塞无关条文给前端。"""
        cited = []
        for la in searched_laws:
            # 匹配 "《劳动法》第四十七条" 或 "劳动合同法第47条" 等引用格式
            law_short = la.law.replace("中华人民共和国", "").replace("劳动法", "").replace("合同法", "")
            patterns = [
                f"《{la.law}》\\s*第\\s*{la.article.replace('第','').replace('条','')}\\s*条",
                f"{la.law}\\s*第\\s*{la.article.replace('第','').replace('条','')}\\s*条",
                la.article,
            ]
            for pat in patterns:
                if re.search(pat, response_text):
                    cited.append({
                        "law": la.law,
                        "article": la.article,
                        "content": la.content[:100],
                    })
                    break
        # 兜底：如果一个都没匹配到，返回前 5 条（避免前端空引用）
        return cited[:10] if cited else [
            {"law": la.law, "article": la.article, "content": la.content[:100]}
            for la in searched_laws[:5]
        ]

    def _build_user_message(self, ctx: AgentContext) -> str:
        parts = []
        if ctx.case_profile:
            parts.append(f"## 用户信息\n{ctx.case_profile}")
        parts.append(f"## 用户问题\n{ctx.user_message}")
        return "\n\n".join(parts)

    def _extract_structured(self, content: str) -> dict:
        """从 LLM 输出的 Markdown 中提取结构化数据。

        增强规则：
        1. 提取金额 —— 匹配「XX 元」「¥XX」
        2. 提取违法类型 —— 匹配「违法」「违反」「不合法」
        3. 提取风险等级 —— 匹配「高/中/低/严重风险」
        4. 提取法条引用 —— 匹配「《XX法》第X条」
        """
        data: dict = {}

        if self.name == "compensation":
            data = self._parse_compensation(content)
        elif self.name == "violation_detect":
            data = self._parse_violations(content)

        # 通用提取
        # 风险等级
        risk_match = re.search(r"风险[等级评定评级]*[：:]\s*(严重|高|中|低)", content)
        if risk_match:
            level_map = {"严重": "critical", "高": "high", "中": "medium", "低": "low"}
            data["risk_level"] = level_map.get(risk_match.group(1), risk_match.group(1))

        # 可主张金额（通用）
        amounts = re.findall(r"可主张[^：:]*[：:]\s*[¥￥]?\s*([\d,]+\.?\d*)\s*元?\s*[~～-]+\s*[¥￥]?\s*([\d,]+\.?\d*)", content)
        if amounts:
            try:
                data["claim_min"] = float(amounts[0][0].replace(",", ""))
                data["claim_max"] = float(amounts[0][1].replace(",", ""))
            except (ValueError, IndexError):
                pass

        # 法条引用
        law_refs = re.findall(r"《([^》]+)》\s*第\s*([\d一二三四五六七八九十]+)\s*条", content)
        if law_refs:
            data["laws_cited"] = [{"law": l[0], "article": l[1]} for l in law_refs[:10]]

        return data

    def _parse_compensation(self, content: str) -> dict:
        """从赔偿计算输出中解析结构化金额。"""
        items = []
        # 匹配行: | 双倍工资 | ¥X | ¥Y | ...
        rows = re.findall(r"\|\s*(.{2,20}?)\s*\|\s*[¥￥]?\s*([\d,]+\.?\d*)\s*\|\s*[¥￥]?\s*([\d,]+\.?\d*)\s*\|", content)
        for row in rows:
            try:
                items.append({
                    "category": row[0].strip(),
                    "min": float(row[1].replace(",", "")),
                    "max": float(row[2].replace(",", "")),
                })
            except (ValueError, IndexError):
                continue

        # 合计
        total = re.search(r"合\s*计[^¥]*[¥￥]?\s*([\d,]+\.?\d*)\s*[^¥]*[¥￥]?\s*([\d,]+\.?\d*)", content)
        result = {"items": items}
        if total:
            try:
                result["total_min"] = float(total.group(1).replace(",", ""))
                result["total_max"] = float(total.group(2).replace(",", ""))
            except (ValueError, IndexError):
                pass
        return result

    def _parse_violations(self, content: str) -> dict:
        """从违法识别输出中解析违法行为列表。"""
        violations = []
        # 匹配 "违法项 N: [类型]"
        lines = content.split("\n")
        current = None
        for line in lines:
            m = re.match(r"#+\s*违法项\s*\d*\s*[:：]\s*(.+)", line)
            if m:
                if current:
                    violations.append(current)
                current = {"type": m.group(1).strip()}
                continue
            if current:
                if "违法" in line and ("✅" in line or "❌" in line or "⚠️" in line):
                    current["verdict"] = "violation" if "违法" in line and "不" not in line[:line.index("违法")] else "legal"
                lawful = re.search(r"法律依据[：:]\s*(.+)", line)
                if lawful:
                    current["law_basis"] = lawful.group(1).strip()
        if current:
            violations.append(current)
        return {"violations": violations}
