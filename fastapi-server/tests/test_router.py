from app.agents.router import IntentRouter


def test_router_violation_detect():
    agents = IntentRouter.route("公司拖欠我工资，这是违法的吗")
    assert "violation_detect" in agents
    assert "compensation" in agents  # 提到工资 → 赔偿计算


def test_router_arbitration():
    agents = IntentRouter.route("我想去劳动仲裁告公司")
    assert "arbitration" in agents


def test_router_default():
    agents = IntentRouter.route("你好")
    assert agents == ["case_analysis"]
