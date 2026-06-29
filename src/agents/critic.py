"""
Critic Agent: quality evaluation and final decision.
"""
from ..models.llm_provider import get_llm_provider
from ..models.schemas import AgentState


def evaluate(state: AgentState) -> AgentState:
    """Score the recommendation and choose auto-send/human-confirm/reject."""
    if state["classification"] != "退货":
        state["execution_logs"].append(
            {
                "agent": "critic",
                "action": "跳过评估",
                "decision": state.get("final_action", "human_confirm"),
            }
        )
        return state

    if not state.get("recommendation"):
        state["eval_score"] = 0.0
        state["final_action"] = "reject"
        return state

    prompt = f"""
原始工单：{state['ticket_content']}

系统生成的处理建议：{state['recommendation']}

订单数据：{state.get('order_data', {})}

退货/售后政策：{state.get('policy_info', '')}

请评分这个建议（0-100）：
- 是否符合公司政策？
- 客户会不会满意？
- 是否存在金额、承诺、流程上的明显风险？
- 是否适合自动发送？

回复格式：
{{
    "score": 85,
    "reasoning": "...",
    "should_auto_send": true,
    "issues": []
}}
"""

    result = get_llm_provider().call_with_json(prompt)
    score = float(result.get("score", 50))

    state["eval_score"] = score

    if score >= 85 and result.get("should_auto_send", True):
        state["final_action"] = "auto_send"
    elif score >= 60:
        state["final_action"] = "human_confirm"
    else:
        state["final_action"] = "reject"

    print(f"[Critic] 评分：{score}/100，决策：{state['final_action']}")

    state["execution_logs"].append(
        {
            "agent": "critic",
            "action": "多维度质量评估",
            "score": score,
            "decision": state["final_action"],
            "result": result,
        }
    )

    return state
