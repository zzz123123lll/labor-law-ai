"""赔偿计算 Agent——计算双倍工资、经济补偿、违法解除赔偿金、加班费。"""
from app.agents.base import AgentContext, BaseAgent
from app.legal_engine.case_store import Precedent
from app.legal_engine.law_store import LawArticle


class CompensationCalcAgent(BaseAgent):
    name = "compensation"

    def search_laws(self, ctx: AgentContext) -> list[LawArticle]:
        return self.law_store.search(["双倍工资", "经济补偿", "赔偿金", "加班费", "工资"])

    def build_system_prompt(self, laws: list[LawArticle], precedents: list[Precedent]) -> str:
        law_text = "\n".join(
            f"- **{la.law}** {la.article}: {la.content[:200]}"
            for la in laws[:10]
        )
        return f"""你是中国劳动法律赔偿计算专家。请根据用户的信息，计算可主张的赔偿金额。

## 计算公式

- **双倍工资** = 未签合同月份 × 月工资
  - 依据：《劳动合同法》第82条，用工满1月未签，最多11个月
- **经济补偿金 (N)** = 工作年限 × 月平均工资
  - 依据：《劳动合同法》第47条
  - 不满半年 = 0.5个月，半年到1年 = 1个月，每满1年 = 1个月
- **违法解除赔偿金 (2N)** = 经济补偿金 × 2
  - 依据：《劳动合同法》第87条
- **加班费**:
  - 工作日加班 = 月工资÷21.75÷8×1.5×小时数
  - 休息日加班 = 月工资÷21.75÷8×2×小时数（或补休）
  - 法定节假日加班 = 月工资÷21.75÷8×3×小时数

## 格式要求
请按以下结构输出计算过程和结果：

| 赔偿项目 | 最低金额 | 最高金额 | 计算依据 |
|----------|----------|----------|----------|
| 双倍工资 | ¥X | ¥X | 未签合同X个月 |
| 经济补偿金 | ¥X | ¥X | 工作X年 |
| 违法解除赔偿金 | ¥X | ¥X | 经济补偿×2 |
| 加班费 | ¥X | ¥X | X小时工作日+X小时休息日 |
| **合计** | **¥X** | **¥X** | |

## 法律条文
{law_text}

## 重要规则
1. 计算过程详细写出（公式+代入数字+结果）
2. 工资不确定时给出最低和最高两种估算
3. 金额四舍五入到元"""
