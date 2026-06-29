from datetime import datetime
from typing import List, NotRequired, Optional, TypedDict


class AgentState(TypedDict):
    """Shared state passed through the Agent workflow."""

    # Input
    ticket_id: str
    ticket_content: str
    customer_id: NotRequired[Optional[str]]
    order_id: NotRequired[Optional[str]]

    # Intermediate results
    classification: Optional[str]
    classification_score: Optional[float]
    customer_data: NotRequired[Optional[dict]]
    order_data: Optional[dict]
    policy_info: Optional[str]
    policy_plan: NotRequired[Optional[dict]]

    # Output
    recommendation: Optional[str]
    eval_score: Optional[float]
    final_action: Optional[str]

    # Metadata
    execution_logs: List[dict]
    created_at: datetime
