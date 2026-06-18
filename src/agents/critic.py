# src/agents/critic.py
"""
Critic Agent：质量评估与最终决策
"""
from ..models.llm_provider import get_llm_provider
from ..models.schemas import AgentState

llm = get_llm_provider("gpt35")

def evaluate(state: AgentState) -> AgentState:
    """
    第四步：评估建议质量，决定是否自动发送
    """
    if not state.get('recommendation'):
        state['final_action'] = "reject"
        return state
    
    prompt = f"""
    原始工单：{state['ticket_content']}
    
    系统生成的处理建议：{state['recommendation']}
    
    请评分这个建议（0-100）：
    - 是否符合公司政策？
    - 客户会不会满意？
    - 有没有明显的错误？
    
    给出一个综合评分。
    
    回复格式：
    {{
        "score": 85,
        "reasoning": "...",
        "should_auto_send": true/false,
        "issues": []
    }}
    """
    
    result = llm.call_with_json(prompt)
    score = result.get('score', 50)
    
    state['eval_score'] = score
    
    # 决策逻辑
    if score >= 75:
        state['final_action'] = "auto_send"
    elif score >= 50:
        state['final_action'] = "human_confirm"
    else:
        state['final_action'] = "reject"
    
    print(f"[Critic] 评分：{score}/100，决策：{state['final_action']}")
    
    state['execution_logs'].append({
        'agent': 'critic',
        'action': '评估',
        'score': score,
        'decision': state['final_action'],
    })
    
    return state