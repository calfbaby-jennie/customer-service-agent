def get_customer_profile(customer_id: str | None) -> dict:
    """Mock CRM/Salesforce lookup."""
    return {
        "customer_id": customer_id or "CUST-DEMO",
        "tier": "gold",
        "satisfaction_score": 85,
        "risk_level": "low",
    }
