"""
Policy Agent: task decomposition and workflow planning.
"""
from ..models.llm_provider import get_llm_provider
from ..models.schemas import AgentState
from ..tools.registry import call_tool


def plan(state: AgentState) -> AgentState:
    """Plan the workflow for return/after-sales tickets."""
    if state["classification"] != "退货":
        print("[Policy] 非退货/售后工单，转人工或其他客服队列")
        state["recommendation"] = "该工单不属于退货/售后自动化范围，建议转人工或对应客服队列处理。"
        state["eval_score"] = 0.0
        state["final_action"] = "human_confirm"
        state["execution_logs"].append(
            {
                "agent": "policy",
                "action": "路由",
                "result": "非退货/售后工单，转人工确认",
            }
        )
        return state

    state["customer_data"] = call_tool("crm.customer_profile", state.get("customer_id"))
    state["order_data"] = call_tool("erp.order_lookup", state.get("order_id"))
    state["policy_info"] = call_tool("kb.return_policy", state["ticket_content"])

    prompt = f"""
客户工单：{state['ticket_content']}

客户信息：{state.get('customer_data', {})}

订单信息：{state.get('order_data', {})}

公司退货/售后政策：{state.get('policy_info', '')}

请规划处理方案：
1. 是否符合退货/售后自动化处理条件？
2. 建议的处理步骤是什么？
3. 是否需要补偿，补偿方案是什么？
4. 哪些情况需要人工确认？

回复格式：
{{
    "eligible": true,
    "steps": ["步骤1", "步骤2"],
    "compensation": "...",
    "manual_review_required": false
}}
"""

    result = get_llm_provider().call_with_json(prompt)
    state["policy_plan"] = result

    print(f"[Policy] 规划完成，符合自动化条件：{result.get('eligible')}")

    state["execution_logs"].append(
        {
            "agent": "policy",
            "action": "任务分解与工作流规划",
            "result": result,
        }
    )

    return state
