from .crm import get_customer_profile
from .knowledge_base import search_return_policy
from .order_system import get_order
from .ticket_system import build_ticket_update


TOOLS = {
    "crm.customer_profile": get_customer_profile,
    "erp.order_lookup": get_order,
    "kb.return_policy": search_return_policy,
    "jira.ticket_update": build_ticket_update,
}


def call_tool(name: str, *args, **kwargs):
    """Call a registered integration tool by name."""
    tool = TOOLS.get(name)
    if not tool:
        raise KeyError(f"Unknown tool: {name}")
    return tool(*args, **kwargs)
