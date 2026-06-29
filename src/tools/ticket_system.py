def build_ticket_update(ticket_id: str, final_action: str | None) -> dict:
    """Mock Jira update payload builder."""
    return {
        "ticket_id": ticket_id,
        "status": final_action or "pending",
        "system": "jira",
    }
