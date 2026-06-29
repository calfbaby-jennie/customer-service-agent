"""
Agent workflow executor.

Uses LangGraph when the dependency is installed. A sequential fallback is kept so
local smoke tests can run before installing the full dependency set.
"""
from __future__ import annotations

from datetime import datetime
from functools import lru_cache
from typing import Optional

from ..models.schemas import AgentState
from .action import execute
from .critic import evaluate
from .policy import plan
from .supervisor import supervise


def _initial_state(
    ticket_id: str,
    ticket_content: str,
    customer_id: Optional[str] = None,
    order_id: Optional[str] = None,
) -> AgentState:
    return AgentState(
        ticket_id=ticket_id,
        ticket_content=ticket_content,
        customer_id=customer_id,
        order_id=order_id,
        classification=None,
        classification_score=None,
        customer_data=None,
        order_data=None,
        policy_info=None,
        policy_plan=None,
        recommendation=None,
        eval_score=None,
        final_action=None,
        execution_logs=[],
        created_at=datetime.utcnow(),
    )


@lru_cache(maxsize=1)
def _build_graph():
    try:
        from langgraph.graph import END, StateGraph
    except ImportError:
        return None

    workflow = StateGraph(AgentState)
    workflow.add_node("supervisor", supervise)
    workflow.add_node("policy", plan)
    workflow.add_node("action", execute)
    workflow.add_node("critic", evaluate)

    workflow.set_entry_point("supervisor")
    workflow.add_edge("supervisor", "policy")
    workflow.add_edge("policy", "action")
    workflow.add_edge("action", "critic")
    workflow.add_edge("critic", END)

    return workflow.compile()


def _run_sequential(state: AgentState) -> AgentState:
    state = supervise(state)
    state = plan(state)
    state = execute(state)
    state = evaluate(state)
    return state


async def run_agent_pipeline(
    ticket_id: str,
    ticket_content: str,
    customer_id: Optional[str] = None,
    order_id: Optional[str] = None,
) -> AgentState:
    """Run the complete Supervisor -> Policy -> Action -> Critic workflow."""
    state = _initial_state(
        ticket_id=ticket_id,
        ticket_content=ticket_content,
        customer_id=customer_id,
        order_id=order_id,
    )

    print(f"\n=== Processing Ticket {ticket_id} ===")

    graph = _build_graph()
    if graph is not None:
        print("→ LangGraph workflow...")
        state = await graph.ainvoke(state)
    else:
        print("→ Sequential workflow fallback...")
        state = _run_sequential(state)

    print(f"\n✓ Final Action: {state['final_action']}")
    print(f"✓ Eval Score: {state.get('eval_score')}/100")
    print(f"✓ Logs: {len(state['execution_logs'])} entries")

    return state
