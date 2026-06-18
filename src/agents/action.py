# src/agents/action.py
"""
Action Agent：执行决策生成建议
"""
from ..models.llm_provider import get_llm_provider
from ..models.schemas import AgentState

llm = get_llm_provider("gpt35")

def execute(state: AgentState) -> AgentState:
    """
    第三步：基于规划生成具体的处理建议
    """
    if state['final_action'] == "skip":
        return state
    
    prompt = f"""
    工单内容：{state['ticket_content']}
    
    订单数据：{state.get('order_data', {})}
    
    政策信息：{state.get('policy_info', '')}
    
    请生成一个处理建议，包括：
    1. 是否批准退货
    2. 退款金额
    3. 需要客户做什么
    4. 我们会做什么
    
    尽可能友好和专业。
    """
    
    recommendation = llm.call(prompt)
    state['recommendation'] = recommendation
    
    print(f"[Action] 建议已生成")
    print(f"建议内容：{recommendation[:100]}...")
    
    state['execution_logs'].append({
        'agent': 'action',
        'action': '生成建议',
        'result': recommendation,
    })
    
    return state