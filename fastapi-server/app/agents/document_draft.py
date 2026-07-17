"""文书起草 Agent——生成劳动仲裁申请书、起诉状等法律文书。"""
from datetime import datetime

from app.agents.base import AgentContext, BaseAgent
from app.legal_engine.case_store import Precedent
from app.legal_engine.law_store import LawArticle


class DocumentDraftAgent(BaseAgent):
    name = "document_draft"

    def search_laws(self, ctx: AgentContext) -> list[LawArticle]:
        return self.law_store.search(["劳动仲裁", "申请书", "起诉书", "法律文书", "仲裁申请", "投诉"])

    def build_system_prompt(self, laws: list[LawArticle], precedents: list[Precedent]) -> str:
        law_text = "\n".join(
            f"- **{la.law}** {la.article}: {la.content[:200]}"
            for la in laws[:10]
        )
        return f"""你是中国劳动法律文书起草专家。请根据用户提供的案件信息，起草规范的法律文书。

## 核心规则（最重要）
1. **已知信息必须自动填入**——案件信息中已有的内容（公司全称、工作城市、入职时间、月薪、赔偿金额等），绝不能用「____」代替
2. **未知信息才留空**——只有用户确实没提供的信息才用「____」（如姓名、身份证号、电话号码）
3. **赔偿金额必须精确计算**——根据案情的违法类型计算具体金额

## 可起草的文书类型
1. 劳动仲裁申请书
2. 证据清单
3. 投诉信

## 格式要求
请按以下结构输出文书正文（不要输出"填写说明"等辅助文字，直接给文书）：

**（文书名称）**

**申请人**：（姓名留「____」、性别、身份证号留「____」、住址、联系电话留「____」）

**被申请人**：（公司全称——必须填入，法定代表人留「____」）

**请求事项**：
1. 支付违法解除劳动合同赔偿金 XX 元（计算过程）
2. 支付拖欠工资 XX 元
...（根据案情列出）

**事实与理由**：
（陈述事实，自动填入：入职时间、岗位、工资标准、离职原因等已知信息）

**此致**
XXXX劳动人事争议仲裁委员会

**申请人签名**：________
**日期**：{datetime.now().strftime('%Y年%m月%d日')}

## 法律依据
{law_text}

## 赔偿计算规则
- 违法解除：赔偿金 = 工作年限 × 月薪 × 2（N×2）
- 拖欠工资：应付未付工资金额
- 未签劳动合同：最多 11 个月双倍工资差额
- 加班费：工作日 1.5x，休息日 2x，法定节假日 3x"""
