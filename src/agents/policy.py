# src/agents/policy.py
"""
Policy Agent：工作流规划
"""
from ..models.llm_provider import get_llm_provider
from ..models.schemas import AgentState

llm = get_llm_provider("gpt35")

def plan(state: AgentState) -> AgentState:
    """
    第二步：如果是退货工单，规划处理流程
    """
    if state['classification'] != "退货":
        print("[Policy] 非退货工单，跳过")
        state['final_action'] = "skip"
        return state
    
    # 这里你可以集成数据库查询
    # 例如：从 state['order_id'] 查询订单信息
    # 这个演示版本用的是硬编码的数据
    
    state['order_data'] = {
        'order_id': 'ORD-12345',
        'status': '待收货',
        'amount': 299.99,
        'created_date': '2024-01-01',
    }
    
    state['policy_info'] = """
    退货政策：
    - 7天无理由退货
    - 商品需完整、未使用
    - 退货费用：买家承担快递费
    """
    
    prompt = f"""
    客户工单：{state['ticket_content']}
    
    订单信息：{state['order_data']}
    
    公司退货政策：{state['policy_info']}
    
    请规划处理方案：
    1. 是否符合退货条件？
    2. 建议的处理步骤是什么？
    3. 可能的补偿方案？
    
    回复格式：
    {{
        "eligible": true/false,
        "steps": ["步骤1", "步骤2"],
        "compensation": "..."
    }}
    """
    
    result = llm.call_with_json(prompt)
    
    print(f"[Policy] 规划完成，符合条件：{result.get('eligible')}")
    
    state['execution_logs'].append({
        'agent': 'policy',
        'action': '规划',
        'result': result,
    })
    
    return state