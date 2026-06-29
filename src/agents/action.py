"""
Action Agent: tool orchestration and response recommendation.
"""
from ..models.llm_provider import get_llm_provider
from ..models.schemas import AgentState
from ..tools.registry import call_tool


def execute(state: AgentState) -> AgentState:
    """Generate a concrete customer-service recommendation."""
    if state["classification"] != "退货":
        return state

    prompt = f"""
工单内容：{state['ticket_content']}

客户信息：{state.get('customer_data', {})}

订单数据：{state.get('order_data', {})}

政策信息：{state.get('policy_info', '')}

Policy Agent 规划：{state.get('policy_plan', {})}

请生成一个处理建议，包括：
1. 是否批准退货/退款
2. 退款金额或补偿方案
3. 需要客户补充什么
4. 平台下一步动作
5. 风险提示或需要人工确认的点

语气需要友好、专业、可直接给客服使用。
"""

    recommendation = get_llm_provider().call(prompt)
    state["recommendation"] = recommendation

    ticket_update = call_tool("jira.ticket_update", state["ticket_id"], state.get("final_action"))

    print("[Action] 建议已生成")
    print(f"建议内容：{recommendation[:100]}...")

    state["execution_logs"].append(
        {
            "agent": "action",
            "action": "工具编排与建议生成",
            "result": recommendation,
            "ticket_update": ticket_update,
        }
    )

    return state
