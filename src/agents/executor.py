# src/agents/executor.py
"""
Agent 执行引擎（整合四个 Agent）
"""
from ..models.schemas import AgentState
from datetime import datetime
from .supervisor import supervise
from .policy import plan
from .action import execute
from .critic import evaluate

async def run_agent_pipeline(ticket_id: str, ticket_content: str) -> AgentState:
    """
    执行完整的 Agent 管道
    """
    # 初始化状态
    state = AgentState(
        ticket_id=ticket_id,
        ticket_content=ticket_content,
        classification=None,
        classification_score=None,
        order_data=None,
        policy_info=None,
        recommendation=None,
        eval_score=None,
        final_action=None,
        execution_logs=[],
        created_at=datetime.utcnow(),
    )
    
    print(f"\n=== Processing Ticket {ticket_id} ===")
    
    # Step 1: Supervisor
    print("→ Supervisor...")
    state = supervise(state)
    
    # Step 2: Policy
    print("→ Policy...")
    state = plan(state)
    
    # Step 3: Action
    print("→ Action...")
    state = execute(state)
    
    # Step 4: Critic
    print("→ Critic...")
    state = evaluate(state)
    
    # 打印最终结果
    print(f"\n✓ Final Action: {state['final_action']}")
    print(f"✓ Eval Score: {state['eval_score']}/100")
    print(f"✓ Logs: {len(state['execution_logs'])} entries")
    
    return state