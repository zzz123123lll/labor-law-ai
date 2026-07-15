"""违法识别 Agent——逐条判断公司行为是否违法。"""
from app.agents.base import BaseAgent, AgentContext
from app.legal_engine.law_store import LawArticle
from app.legal_engine.case_store import Precedent


class ViolationDetectAgent(BaseAgent):
    name = "violation_detect"

    def search_laws(self, ctx: AgentContext) -> list[LawArticle]:
        violation_types = ctx.case_profile.get("violation_types", [])
        keywords = violation_types if violation_types else ["违法", "解除", "工资", "加班"]
        return self.law_store.search(keywords)

    def build_system_prompt(self, laws: list[LawArticle], precedents: list[Precedent]) -> str:
        law_text = "\n".join(
            f"- **{la.law}** {la.article}: {la.content[:200]}"
            for la in laws[:10]
        )
        return f"""你是中国劳动法律违法识别专家。请逐条分析用户的描述，判断公司是否存在违法行为。

## 格式要求
请按以下结构逐条输出：

### 违法项 1: [违法类型名称]
- **用户陈述**: 用户说了什么
- **法律规定**: {law_text}
- **事实判断**: 根据用户所述，该行为是否成立
- **违法认定**: ✅ 违法 / ⚠️ 可能违法（需补充证据） / ❌ 证据不足 / ✅ 合法
- **法律依据**: 具体法条编号及原文
- **风险分析**: 如果成立，用户面临什么后果

（如果有多个违法行为，继续 违法项 2、3……）

### 总结
- 明确违法行为: N项
- 可能违法行为: N项
- 建议立即补充的证据

## 法律条文库
{law_text}

## 重要规则
1. 不用标记数字编号，用自然语言
2. 不确定的事说"不确定"，不要编造
3. 区分用户陈述和客观事实"""
