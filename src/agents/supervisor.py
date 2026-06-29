"""
Supervisor Agent: intent understanding and routing.
"""
from ..models.llm_provider import get_llm_provider
from ..models.schemas import AgentState


def supervise(state: AgentState) -> AgentState:
    """Classify the ticket and decide whether it enters the return workflow."""
    prompt = f"""
工单内容：{state['ticket_content']}

请分类这个工单：
- 是否是退货/售后工单？(是/否)
- 如果是退货/售后，给出信心度评分 (0-1)
- 如果不是退货/售后，简短说明原因

回复格式：
{{
    "is_return": true,
    "confidence": 0.95,
    "reason": "..."
}}
"""

    result = get_llm_provider().call_with_json(prompt)

    state["classification"] = "退货" if result.get("is_return") else "其他"
    state["classification_score"] = float(result.get("confidence", 0.5))

    print(
        f"[Supervisor] 分类：{state['classification']} "
        f"(置信度：{state['classification_score']})"
    )

    state["execution_logs"].append(
        {
            "agent": "supervisor",
            "action": "分类与路由",
            "result": {
                "classification": state["classification"],
                "confidence": state["classification_score"],
                "reason": result.get("reason", ""),
            },
        }
    )

    return state
