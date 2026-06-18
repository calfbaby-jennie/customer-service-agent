# src/agents/supervisor.py
"""
Supervisor Agent：工单分类与路由
"""
from ..models.llm_provider import get_llm_provider
from ..models.schemas import AgentState

llm = get_llm_provider("gpt35")

def supervise(state: AgentState) -> AgentState:
    """
    第一步：理解工单内容，决定是否需要处理
    """
    prompt = f"""
    工单内容：{state['ticket_content']}
    
    请分类这个工单：
    - 是否是退货/售后工单？(是/否)
    - 如果是退货，给出信心度评分 (0-1)
    - 如果不是退货，简短说明原因
    
    回复格式：
    {{
        "is_return": true/false,
        "confidence": 0.95,
        "reason": "..."
    }}
    """
    
    result = llm.call_with_json(prompt)
    
    state['classification'] = "退货" if result.get('is_return') else "其他"
    state['classification_score'] = result.get('confidence', 0.5)
    
    print(f"[Supervisor] 分类：{state['classification']} (置信度：{state['classification_score']})")
    
    # 记录执行日志
    state['execution_logs'].append({
        'agent': 'supervisor',
        'action': '分类',
        'result': state['classification'],
    })
    
    return state