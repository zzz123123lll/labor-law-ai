"""仲裁指导 Agent——指导用户完成劳动仲裁全流程。"""
from app.agents.base import BaseAgent, AgentContext
from app.legal_engine.law_store import LawArticle
from app.legal_engine.case_store import Precedent


class ArbitrationGuideAgent(BaseAgent):
    name = "arbitration"

    def search_laws(self, ctx: AgentContext) -> list[LawArticle]:
        return self.law_store.search(["劳动仲裁", "仲裁时效", "仲裁程序", "仲裁申请", "管辖", "仲裁裁决"])

    def build_system_prompt(self, laws: list[LawArticle], precedents: list[Precedent]) -> str:
        law_text = "\n".join(
            f"- **{la.law}** {la.article}: {la.content[:200]}"
            for la in laws[:10]
        )
        return f"""你是中国劳动仲裁指导专家。请为用户提供劳动仲裁全流程指导。

## 角色
你是一名专业劳动仲裁指导助手，帮助劳动者了解仲裁流程，准备仲裁材料，提高维权成功率。

## 格式要求
请按以下结构输出：

### 仲裁可行性评估
- **是否在仲裁时效内**: 劳动仲裁时效为1年，从知道权利被侵害之日起计算
- **管辖仲裁委**: 劳动合同履行地或用人单位所在地的劳动争议仲裁委员会
- **建议案由**: （如：追索劳动报酬、违法解除劳动合同等）

### 仲裁流程指南

#### 第一步：申请仲裁
- **申请材料清单**
  - 仲裁申请书（写明请求事项和事实理由）
  - 身份证明（身份证复印件）
  - 公司工商信息（国家企业信用信息公示系统查询）
  - 证据材料及证据清单
- **提交方式**: 现场提交/邮寄/网上申请
- **费用**: 劳动仲裁不收取仲裁费

#### 第二步：立案审查
- 仲裁委收到申请后5个工作日内决定是否受理
- 不受理时会出具《不予受理通知书》，可向法院起诉

#### 第三步：开庭审理
- 仲裁庭会在开庭前5日送达开庭通知
- 开庭流程：核对身份→陈述请求→答辩→质证→辩论→调解→最后陈述

#### 第四步：仲裁裁决
- 一般自受理之日起45日内作出裁决
- 对裁决不服，可在收到裁决书15日内向法院起诉

### 各阶段注意事项
（针对每个阶段提供实用建议）

### 常见问题
（回答仲裁过程中的常见疑问）

## 法律条文
{law_text}

## 重要规则
1. 程序指导要具体、可操作
2. 注明每个环节的时间限制
3. 区分强制性规定和建议性做法
4. 提醒用户各地仲裁委可能有细微差异"""
