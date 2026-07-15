"""Agent 注册表：按名称获取 Agent 实例。"""
from app.agents.case_analysis import CaseAnalysisAgent
from app.agents.violation_detect import ViolationDetectAgent
from app.agents.compensation_calc import CompensationCalcAgent
from app.agents.contract_review import ContractReviewAgent
from app.agents.evidence_analyze import EvidenceAnalyzeAgent
from app.agents.document_draft import DocumentDraftAgent
from app.agents.arbitration_guide import ArbitrationGuideAgent
from app.agents.strategy_plan import StrategyPlanAgent


class AgentRegistry:
    """管理所有 Agent 实例。"""

    def __init__(self, law_store, case_store):
        self._agents = {
            "case_analysis": CaseAnalysisAgent(law_store, case_store),
            "violation_detect": ViolationDetectAgent(law_store, case_store),
            "compensation": CompensationCalcAgent(law_store, case_store),
            "contract_review": ContractReviewAgent(law_store, case_store),
            "evidence": EvidenceAnalyzeAgent(law_store, case_store),
            "document_draft": DocumentDraftAgent(law_store, case_store),
            "arbitration": ArbitrationGuideAgent(law_store, case_store),
            "strategy": StrategyPlanAgent(law_store, case_store),
        }

    def get(self, name: str):
        return self._agents.get(name)
