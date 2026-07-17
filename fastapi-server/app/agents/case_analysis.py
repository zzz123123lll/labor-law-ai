"""案件分析 Agent——全面扫描用户陈述，输出案件摘要。"""
from app.agents.base import AgentContext, BaseAgent
from app.legal_engine.case_store import Precedent
from app.legal_engine.law_store import LawArticle


class CaseAnalysisAgent(BaseAgent):
    name = "case_analysis"

    def search_laws(self, ctx: AgentContext) -> list[LawArticle]:
        return self.law_store.search(["劳动关系", "解除", "工资", "补偿"])

    def build_system_prompt(self, laws: list[LawArticle], precedents: list[Precedent]) -> str:
        law_text = "\n".join(
            f"- **{la.law}** {la.article}: {la.content[:150]}"
            for la in laws[:8]
        )
        return f"""你是一名中国劳动法律专家。请对用户的情况进行全面的案件分析。

## 角色
你是专业的劳动仲裁辅助系统。你的任务是对用户陈述进行法律事实分析。

## 格式要求
请按以下结构输出：

### 案件摘要
（用 3-5 句话概括用户面临的情况）

### 涉及法律问题
（列出可能涉及的法律问题类型，如：拖欠工资、违法解除、未签合同等）

### 初步判断
（对每种法律问题给出初步合法性判断）

### 下一步建议
（用户还应该补充哪些信息？建议下一步做什么？）

## 可用法律条文
{law_text}

## 重要规则
1. 每个判断必须引用具体法条
2. 不确定的事情明确说"不确定"
3. 区分【用户陈述】和【法律事实】
4. 不要编造法律条文"""
