"""AI Router：规则匹配意图 → 返回应执行的 Agent 列表。"""

ROUTER_RULES: dict[str, list[str]] = {
    "case_analysis":    ["发生了什么", "我该怎么办", "能维权吗", "是不是违法", "被辞退", "被开除"],
    "violation_detect": ["违法", "不合法", "合法吗", "公司可以这样吗", "公司能这样吗"],
    "compensation":     ["赔多少", "赔偿", "多少钱", "双倍工资", "加班费", "经济补偿", "算一下", "计算", "工资"],
    "contract_review":  ["合同", "劳动合同", "试用期", "竞业限制", "签合同", "保密协议"],
    "evidence":         ["证据", "截图", "聊天记录", "录音", "工资条", "打卡"],
    "arbitration":      ["仲裁", "打官司", "告公司", "劳动仲裁", "起诉"],
    "document_draft":   ["写", "申请书", "法律文书", "仲裁书", "投诉信", "帮我写"],
    "strategy":         ["维权步骤", "怎么办", "流程", "路线", "方案", "步骤"],
}


class IntentRouter:
    """基于关键词的意图路由。匹配多个时级联执行。"""

    _CASCADE_ORDER = [
        "case_analysis",
        "violation_detect",
        "compensation",
        "evidence",
        "strategy",
    ]

    @classmethod
    def route(cls, text: str) -> list[str]:
        """返回应执行的 agent 名称列表，按优先级排序。"""
        matched = []
        for agent_name, keywords in ROUTER_RULES.items():
            for kw in keywords:
                if kw in text:
                    matched.append(agent_name)
                    break

        if not matched:
            return ["case_analysis"]  # 默认走案件分析

        # 按级联顺序排列
        ordered = [a for a in cls._CASCADE_ORDER if a in matched]
        # 追加不在级联中的
        for a in matched:
            if a not in ordered:
                ordered.append(a)
        return ordered
