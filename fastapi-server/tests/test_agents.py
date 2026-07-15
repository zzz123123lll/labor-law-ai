"""Agent 注册与功能测试。"""
from app.agents.registry import AgentRegistry
from app.legal_engine.law_store import LawStore
from app.legal_engine.case_store import CaseStore
from app.agents.base import AgentContext


def test_all_agents_registered():
    """验证 8 个 agent 都可用 registry.get(name) 获取。"""
    law_store = LawStore()
    case_store = CaseStore()
    registry = AgentRegistry(law_store, case_store)

    expected = [
        "case_analysis", "violation_detect", "compensation",
        "contract_review", "evidence", "document_draft",
        "arbitration", "strategy",
    ]
    for name in expected:
        agent = registry.get(name)
        assert agent is not None, f"Agent '{name}' 未注册"
        assert agent.name == name, f"Agent '{name}' 的 name 属性不匹配"


def test_case_analysis_search_laws():
    """案件分析 Agent 的 search_laws 返回非空列表。"""
    law_store = LawStore()
    law_store.load("app/legal_engine/data")
    case_store = CaseStore()
    agent = AgentRegistry(law_store, case_store).get("case_analysis")

    laws = agent.search_laws(AgentContext(user_message="被公司无故辞退"))
    assert len(laws) > 0, "案件分析 search_laws 返回空列表"


def test_violation_detect_search_laws():
    """违法识别 Agent 的 search_laws 返回非空列表。"""
    law_store = LawStore()
    law_store.load("app/legal_engine/data")
    case_store = CaseStore()
    agent = AgentRegistry(law_store, case_store).get("violation_detect")

    laws = agent.search_laws(AgentContext(
        user_message="公司拖欠工资",
        case_profile={"violation_types": ["拖欠工资", "违法解除"]},
    ))
    assert len(laws) > 0, "违法识别 search_laws 返回空列表"


def test_compensation_search_laws():
    """赔偿计算 Agent 的 search_laws 返回非空列表。"""
    law_store = LawStore()
    law_store.load("app/legal_engine/data")
    case_store = CaseStore()
    agent = AgentRegistry(law_store, case_store).get("compensation")

    laws = agent.search_laws(AgentContext(user_message="被辞退能赔多少钱"))
    assert len(laws) > 0, "赔偿计算 search_laws 返回空列表"


def test_contract_review_search_laws():
    """合同审查 Agent 的 search_laws 返回非空列表。"""
    law_store = LawStore()
    law_store.load("app/legal_engine/data")
    case_store = CaseStore()
    agent = AgentRegistry(law_store, case_store).get("contract_review")

    laws = agent.search_laws(AgentContext(user_message="公司让我签劳动合同"))
    assert len(laws) > 0, "合同审查 search_laws 返回空列表"


def test_evidence_search_laws():
    """证据分析 Agent 的 search_laws 返回非空列表。"""
    law_store = LawStore()
    law_store.load("app/legal_engine/data")
    case_store = CaseStore()
    agent = AgentRegistry(law_store, case_store).get("evidence")

    laws = agent.search_laws(AgentContext(user_message="我有聊天记录和工资条"))
    assert len(laws) > 0, "证据分析 search_laws 返回空列表"


def test_document_draft_search_laws():
    """文书起草 Agent 的 search_laws 返回非空列表。"""
    law_store = LawStore()
    law_store.load("app/legal_engine/data")
    case_store = CaseStore()
    agent = AgentRegistry(law_store, case_store).get("document_draft")

    laws = agent.search_laws(AgentContext(user_message="帮我写仲裁申请书"))
    assert len(laws) > 0, "文书起草 search_laws 返回空列表"


def test_arbitration_search_laws():
    """仲裁指导 Agent 的 search_laws 返回非空列表。"""
    law_store = LawStore()
    law_store.load("app/legal_engine/data")
    case_store = CaseStore()
    agent = AgentRegistry(law_store, case_store).get("arbitration")

    laws = agent.search_laws(AgentContext(user_message="怎么申请劳动仲裁"))
    assert len(laws) > 0, "仲裁指导 search_laws 返回空列表"


def test_strategy_search_laws():
    """维权路线 Agent 的 search_laws 返回非空列表。"""
    law_store = LawStore()
    law_store.load("app/legal_engine/data")
    case_store = CaseStore()
    agent = AgentRegistry(law_store, case_store).get("strategy")

    laws = agent.search_laws(AgentContext(user_message="公司违法辞退我该怎么办"))
    assert len(laws) > 0, "维权路线 search_laws 返回空列表"
