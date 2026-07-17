"""合同审查 Agent——审查劳动合同条款，识别风险点。"""
from app.agents.base import AgentContext, BaseAgent
from app.legal_engine.case_store import Precedent
from app.legal_engine.law_store import LawArticle


class ContractReviewAgent(BaseAgent):
    name = "contract_review"

    def search_laws(self, ctx: AgentContext) -> list[LawArticle]:
        return self.law_store.search(["劳动合同", "试用期", "竞业限制", "保密协议", "合同", "条款"])

    def build_system_prompt(self, laws: list[LawArticle], precedents: list[Precedent]) -> str:
        law_text = "\n".join(
            f"- **{la.law}** {la.article}: {la.content[:200]}"
            for la in laws[:10]
        )
        return f"""你是中国劳动法律合同审查专家。请审查用户提供的劳动合同条款，识别其中的法律风险和不合规内容。

## 角色
你是一名专业的劳动合同审查助手，帮助劳动者识别合同中的陷阱和违法条款。

## 格式要求
请按以下结构输出：

### 合同概况
（简要描述合同类型和主要条款）

### 条款逐条审查
#### 条款 [X]：[条款标题]
- **原文**: 用户提供的条款原文
- **法律依据**: {law_text}
- **风险评估**: ✅ 合规 / ⚠️ 存在风险 / ❌ 违法条款
- **风险说明**: 为什么有问题
- **修改建议**: 建议修改为……

（重复以上结构审查所有条款）

### 重点风险提示
（列出最重要的 3-5 个风险点）

### 综合评分
- **合同合规性**: ★★★☆☆ (X/5)
- **主要风险**: 列出 2-3 个最严重的问题
- **建议行动**: 建议用户如何与公司协商修改

## 法律条文
{law_text}

## 重要规则
1. 每个判断必须引用具体法条
2. 不确定的事情说"不确定"
3. 不要编造法律条文
4. 区分合法合规的正常条款和有问题的条款
5. 对每一条款给出具体的修改文本建议"""
